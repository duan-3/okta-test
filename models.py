from app import db

class OktaUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sessionID = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=True)