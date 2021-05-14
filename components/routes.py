import logging
from time import sleep

import jsonschema.exceptions
from flask import request
from jsonschema import validate

from components import app
from components.models import *
from components.processqueries import ProcessQueries
from extra import paramvalidatormodel


@app.route('/create', methods=["POST"])
def create():
    obj_routes = Routes()
    return obj_routes.determine_create_file_method()


@app.route('/update', methods=["PATCH"])
def update():
    obj_routes = Routes()
    return obj_routes.determine_update_file_method()


@app.route('/get', methods=["GET"])
def get():
    obj_routes = Routes()
    file_id = request.args.get("id", None)
    return obj_routes.get_audio_list(file_id)


@app.route('/delete', methods=["DELETE"])
def delete():
    obj_routes = Routes()
    file_id = request.args.get("id", None)
    return obj_routes.delete(file_id)


class Routes(ProcessQueries):
    file_type_code = None
    successful_response = '{"status_code":"200","message": "Successful"}'
    successful_response_get = '{"status_code":"200","message": "Successful", "data": %s}'
    bad_request_response_structure = '{"status_code":"400","message": "Bad Request", "details": "%s"}'
    bad_request_response = bad_request_response_structure % "file type code is not present"
    error_response_structure = '{"status_code":"500","message": "Internal Server Error", "details": "%s"}'
    error_response_file_not_present = '{"status_code":"500","message": "Internal Server Error", "details": "%s"}'
    param_validator = {}
    __retry_count__ = 3
    __retry_sleep_interval_sec__ = 0.5

    def __init__(self):
        super().__init__()
        self.request_body_params = request.get_json()

    def validate_upload_params(self):
        self.request_body_params = request.get_json()
        self.file_type_code = self.request_body_params.get("fileTypeCode")
        if self.request_body_params not in [None, ""]:
            constant = paramvalidatormodel.Constant()
            self.param_validator = constant.upload_api_param_validation.get(self.file_type_code, None)
            if self.param_validator:
                try:
                    validate(instance=self.request_body_params, schema=self.param_validator)
                    return True
                except jsonschema.exceptions.ValidationError as e:
                    raise e
            else:
                return False

    def determine_create_file_method(self):
        try:
            if self.validate_upload_params():
                if self.file_type_code == 1:
                    return self.create_song_file()
                elif self.file_type_code == 2:
                    return self.create_audio_book_file()
                elif self.file_type_code == 3:
                    return self.create_podcast_file()
            else:
                return self.bad_request_response
        except jsonschema.exceptions.ValidationError as e:
            return self.bad_request_response_structure % e.message

    def determine_update_file_method(self):
        try:
            if self.validate_upload_params():
                if self.file_type_code == 1:
                    return self.update_song_file()
                elif self.file_type_code == 2:
                    return self.update_audio_book_file()
                elif self.file_type_code == 3:
                    return self.update_podcast_file()
            else:
                return self.bad_request_response
        except jsonschema.exceptions.ValidationError as e:
            return self.bad_request_response_structure % e.message

    def create_audio_file(self):
        try:
            file_to_create = AudioFiles(fileName=self.request_body_params.get("name"),
                                        duration=self.request_body_params.get("duration"),
                                        uploadedTime=self.request_body_params.get("uploadedTime"),
                                        audioFileType=self.request_body_params.get("fileTypeCode"))
            file_id = self.create_record(file_to_create)
            if self.retry_insert(file_id, file_to_create, 'audio_files'):
                return file_id
            else:
                return None
        except Exception as e:
            logging.error("Was not able to insert data into audio_files table", exc_info=e)
            self.rollback()
            raise

    def retry_insert(self, file_id, data, table_name):
        attempts = 0
        while file_id is None and attempts < self.__retry_count__:
            logging.debug(
                "MySQL connection lost - sleeping for %.2f sec and will retry (attempt #%d)",
                self.__retry_sleep_interval_sec__, attempts
            )
            sleep(self.__retry_sleep_interval_sec__)
            db.session.refresh(data)
            file_id = data.id
            attempts += 1
        if file_id is None:
            logging.error(f"Was not able to insert data into {table_name} table")
            self.rollback()
            return False
        else:
            return True

    def create_song_file(self):
        try:
            file_id = self.create_audio_file()
            if file_id is not None:
                insert_foreign_key_in_additional_data = SongFileAdditionalData(fileId=file_id)
                additional_id = self.create_record(insert_foreign_key_in_additional_data)
                if self.retry_insert(additional_id, insert_foreign_key_in_additional_data, "song_file_additional_data"):
                    return self.successful_response
                else:
                    return self.error_response_structure % "insertion failed in song_file_additional_data"
            else:
                return self.error_response_structure % "insertion failed in audio_files"
        except Exception as e:
            logging.error("Was not able to insert data into song_file_additional_data table: %s" % e)
            self.rollback()
            return self.error_response_structure % "Unknown"

    def create_audio_book_file(self):
        try:
            file_id = self.create_audio_file()
            if file_id is not None:
                insert_foreign_key_in_additional_data = AudioBookAdditionalData(fileId=file_id,
                                                                                audioBookTitleAuthor=self.request_body_params.get(
                                                                                    "audioBookTitleAuthor"),
                                                                                audioBookNarrator=self.request_body_params.get(
                                                                                    "audioBookNarrator"))
                additional_id = self.create_record(insert_foreign_key_in_additional_data)
                if self.retry_insert(additional_id, insert_foreign_key_in_additional_data,
                                     "audio_book_additional_data"):
                    return self.successful_response
                else:
                    return self.error_response_structure % "insertion failed in audio_book_additional_data"
            return self.error_response_structure % "insertion failed in audio_files"
        except Exception as e:
            logging.error("Was not able to insert data into audio_files table: %s" % e)
            self.rollback()
            return self.error_response_structure % "Unknown"

    def create_podcast_file(self):
        podcast_participant_id = None
        try:
            file_id = self.create_audio_file()
            if file_id is not None:
                insert_foreign_key_in_additional_data = PodCastFileAdditionalData(fileId=file_id,
                                                                                  podcastHost=self.request_body_params.get(
                                                                                      "podcastHost"))
                podcast_file_additional_data_id = self.create_record(insert_foreign_key_in_additional_data)
                if self.retry_insert(podcast_file_additional_data_id, insert_foreign_key_in_additional_data,
                                     "pod_cast_file_additional_data"):
                    for podcast_participants in self.request_body_params.get("podcastParticipants"):
                        participants_in_podcast = PodCastParticipants(podcastId=podcast_file_additional_data_id,
                                                                      podcastParticipantName=podcast_participants)
                        podcast_participant_id = self.create_record(participants_in_podcast)
                        if self.retry_insert(podcast_participant_id, participants_in_podcast,
                                             "pod_cast_participants"):
                            continue
                        else:
                            break
                    if podcast_participant_id:
                        return self.successful_response
                    else:
                        self.rollback()
                        return self.error_response_structure % "insertion failed in pod_cast_participants"
                else:
                    self.rollback()
                    return self.error_response_structure % "insertion failed in pod_cast_file_additional_data"
            else:
                self.rollback()
                return self.error_response_structure % "insertion failed in audio_files"
        except Exception as e:
            logging.error("Was not able to insert data into podcast_file_additional_data table: %s" % e)
            self.rollback()
            return self.error_response_structure % "Unknown"

    def update_audio_file(self):
        try:
            file_id = int(request.args.get("id"))
            file_id = self.select_record(table=AudioFiles, filter_by=file_id)
            if file_id is not None:
                update_dict = {"fileName": self.request_body_params.get("name"),
                               "duration": self.request_body_params.get("duration"),
                               "uploadedTime": self.request_body_params.get("uploadedTime"),
                               "audioFileType": self.request_body_params.get("fileTypeCode")}
                update_id = self.update_record(AudioFiles, AudioFiles(id=file_id), update_dict)
                if update_id is not None:
                    return update_id
                else:
                    self.rollback()
            else:
                return False
        except Exception as e:
            logging.error("Was not able to update data into audio_files table: %s" % e)
            self.rollback()
            raise

    def update_song_file(self):
        try:
            if self.update_audio_file():
                return self.successful_response
            else:
                string = self.error_response_file_not_present % "file not present"
                return string
        except Exception as e:
            logging.error("Was not able to update data into song_file_additional_data table: %s" % e)
            self.rollback()
            return self.error_response_structure % "Unknown"

    def update_audio_book_file(self):
        try:
            update_id = self.update_audio_file()
            if update_id is not None:
                additional_id = self.select_record_backref(AudioBookAdditionalData, update_id)
                update_dict = {"audioBookTitleAuthor": self.request_body_params.get("audioBookTitleAuthor"),
                               "audioBookNarrator": self.request_body_params.get("audioBookNarrator")}
                if self.update_record(AudioBookAdditionalData, AudioBookAdditionalData(id=additional_id),
                                      update_dict) is not None:
                    return self.successful_response
            else:
                return self.error_response_file_not_present % "file not present"
        except Exception as e:
            logging.error("Was not able to update data into audio_book_file_additional_data table: %s" % e)
            self.rollback()
            return self.error_response_structure % "Unknown"

    def update_podcast_file(self):
        podcast_participant_id = None
        participants_list = self.request_body_params.get("podcastParticipants")
        podcast_id = None
        try:
            update_id = self.update_audio_file()
            if update_id is not None:
                additional_id = self.select_record_backref(PodCastFileAdditionalData, update_id)
                update_dict = {"podcastHost": self.request_body_params.get("podcastHost")}
                if self.update_record(PodCastFileAdditionalData, PodCastFileAdditionalData(id=additional_id),
                                      update_dict) is not None:
                    podcast_id_list = self.select_record_podcast_participants(PodCastParticipants, additional_id)
                    for podcast_id in podcast_id_list:
                        self.delete_record(PodCastParticipants, podcast_id)
                    for participants in participants_list:
                        update_dict_participants = {"podcastParticipantName": participants}
                        podcast_participant_id = self.update_record(PodCastParticipants,
                                                                    PodCastParticipants(podcastId=podcast_id),
                                                                    update_dict_participants)
                        if podcast_participant_id:
                            continue
                        else:
                            break
                    if podcast_participant_id:
                        return self.successful_response
                    else:
                        self.rollback()
                        return self.error_response_structure % "updating failed in pod_cast_participants"
                else:
                    self.rollback()
                    return self.error_response_structure % "updating failed in pod_cast_file_additional_data"
            else:
                self.rollback()
                return self.error_response_structure % "updating failed in audio_files"
        except Exception as e:
            logging.error("Was not able to update data into podcast_file_additional_data table: %s" % e)
            self.rollback()
            return self.error_response_structure % "Unknown"

    def get_audio_list(self, file_id=None):
        response = []
        podcast_participants_list = []
        i = 0
        try:
            if file_id:
                file_id = int(file_id)
                file_list = self.select_one(AudioFiles, file_id, active=1)
            else:
                file_list = self.select_all(AudioFiles, active=1)
            for file in file_list:

                file_type_result = db.session.query(
                    ConfigFileType, AudioFiles
                ).join(
                    ConfigFileType, AudioFiles.audioFileType == ConfigFileType.id
                ).filter(
                    AudioFiles.id == file.id
                ).all()
                if file.audioFileType == 1:
                    response.append({
                        "fileName": file.fileName,
                        "duration": file.duration,
                        "fileType": file_type_result[i].ConfigFileType.fileType
                    })
                elif file.audioFileType == 2:
                    audio_book_details = db.session.query(
                        AudioFiles, AudioBookAdditionalData
                    ).join(
                        AudioBookAdditionalData, AudioFiles.id == AudioBookAdditionalData.fileId
                    ).filter(
                        AudioFiles.id == file.id
                    ).all()
                    response.append({
                        "fileName": file.fileName,
                        "duration": file.duration,
                        "fileType": file_type_result[i].ConfigFileType.fileType,
                        "audioBookTitleAuthor": audio_book_details[i].AudioBookAdditionalData.audioBookTitleAuthor,
                        "audioBookNarrator": audio_book_details[i].AudioBookAdditionalData.audioBookNarrator
                    })
                elif file.audioFileType == 3:
                    podcast_details = db.session.query(
                        PodCastFileAdditionalData, AudioFiles, PodCastParticipants
                    ).join(
                        PodCastFileAdditionalData, AudioFiles.id == PodCastFileAdditionalData.fileId
                    ).outerjoin(
                        PodCastParticipants, PodCastParticipants.podcastId == PodCastFileAdditionalData.id
                    ).filter(
                        AudioFiles.id == file.id
                    ).all()
                    for podcast in podcast_details:
                        podcast_participants_list.append(podcast.PodCastParticipants.podcastParticipantName)

                    response.append({
                        "fileName": file.fileName,
                        "duration": file.duration,
                        "fileType": file_type_result[i].ConfigFileType.fileType,
                        "podcastHost": podcast_details[i].PodCastFileAdditionalData.podcastHost,
                        "podcastParticipants": podcast_participants_list
                    })
            response = self.successful_response_get % response
            response = response.replace("\'", "\"")
            return response
        except Exception as e:
            logging.error("Was not able to fetch data: %s" % e)
            return self.error_response_structure % "Unknown"

    def delete(self, file_id):
        try:
            file_id = int(file_id)
            file_id = self.select_record(table=AudioFiles, filter_by=file_id)
            if file_id is not None:
                update_dict = {"isActive": 0}
                self.update_record(AudioFiles, AudioFiles(id=file_id), update_dict)
                return self.successful_response
            else:
                return self.error_response_file_not_present % "File Not present"
        except Exception as e:
            logging.error("Was not able to update data into audio_files table: %s" % e)
            self.rollback()
            return self.error_response_structure % "Unknown"
