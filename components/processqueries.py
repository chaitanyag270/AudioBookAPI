from components import db


class ProcessQueries:

    def create_record(self, data_to_create):
        db.session.add(data_to_create)
        db.session.commit()
        db.session.refresh(data_to_create)
        return data_to_create.id

    def update_record(self, table, key_table, update_dict):
        db.session.query(table).filter(table.id == key_table.id).update(update_dict)
        db.session.commit()
        return key_table.id

    def rollback(self):
        db.session.rollback()

    def select_record(self, table, filter_by):
        file_id_list = table.query.filter_by(id=filter_by)
        for file_id in file_id_list:
            return file_id.id

    def select_record_backref(self, table, filter_by):
        file_id_list = table.query.filter_by(fileId=filter_by)
        for file_id in file_id_list:
            return file_id.id

    def select_record_podcast_participants(self, table, filter_by):
        podcast_id_list = []
        file_id_list = table.query.filter_by(podcastId=filter_by)
        for file_id in file_id_list:
            podcast_id_list.append(file_id.id)
        return podcast_id_list

    def delete_record(self, table, filter_by):
        table.query.filter_by(id=filter_by).delete()
        db.session.commit()

    def select_all(self, table, active):
        return table.query.filter_by(isActive=active)

    def select_one(self, table, file_id, active):
        return table.query.filter_by(id=file_id, isActive=active)

    def get_file_type(self, table, filter_by):
        for file in table.query.filter_by(id=filter_by):
            file.audioFileType
