from .mainModel import db

##Examples of tickets
## Admin access ticket
class TicketModel(db.Model):
    ticketId = db.Column(db.Integer, primary_key=True)
    ticketRequest = db.Column(db.String[100],nullable = False) #Options : Access,Edit
    ticketTarget = db.Column(db.String[100],nullable = False)  #Options: AdminAccess,ManagerAccess,Section
    ticketDetails = db.Column(db.String[100],nullable = True)  #Optional: Details of why the ticket was raised.
    ticketRaisedBy = db.Column(db.Integer,db.ForeignKey('user_model.uuid'),nullable =False)
    action = db.Column(db.String[50],nullable=True)
    