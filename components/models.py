from sqlalchemy.dialects.mysql import BIGINT

from components import db


class ConfigFileType(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fileTypeCode = db.Column(db.Integer(), nullable=False)
    fileType = db.Column(db.String(length=50), nullable=False)


class SongFileAdditionalData(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fileId = db.Column(db.Integer(), db.ForeignKey('audio_files.id'))


class AudioBookAdditionalData(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    audioBookTitleAuthor = db.Column(db.String(length=100), nullable=False)
    audioBookNarrator = db.Column(db.String(length=100), nullable=False)
    fileId = db.Column(db.Integer(), db.ForeignKey('audio_files.id'))


class PodCastFileAdditionalData(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    podcastHost = db.Column(db.String(length=100), nullable=False)
    podcastParticipants = db.relationship('PodCastParticipants', backref='participant_id', lazy=True)
    fileId = db.Column(db.Integer(), db.ForeignKey('audio_files.id'))


class PodCastParticipants(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    podcastId = db.Column(db.Integer(), db.ForeignKey('pod_cast_file_additional_data.id'))
    podcastParticipantName = db.Column(db.String(length=100), nullable=False)


class AudioFiles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    fileName = db.Column(db.String(length=100), nullable=False)
    duration = db.Column(BIGINT(unsigned=True), nullable=False)
    uploadedTime = db.Column(db.DateTime, nullable=False)
    filePath = db.Column(db.String(length=150), nullable=True)
    audioFileType = db.Column(db.Integer(), db.ForeignKey('config_file_type.id'))
    songFile = db.relationship('SongFileAdditionalData', backref='song_file_id', lazy=True)
    audioBookFile = db.relationship('AudioBookAdditionalData', backref='audio_book_file_id', lazy=True)
    podcastFile = db.relationship('PodCastFileAdditionalData', backref='podcast_file_id', lazy=True)
    isActive = db.Column(db.Boolean(), nullable=False, default=1)
