from flask import Flask,jsonify,make_response
import sys
from flask_restful import Api, Resource,reqparse
from flask_restful import inputs
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_restful import fields, marshal_with
from datetime import date
from flask import abort

app = Flask(__name__)

api = Api(app)
parser = reqparse.RequestParser()




#database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database4.db'
# todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class EventList(db.Model):
    __tablename__ = 'Eventlist'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)


resource_fields = {
    'id': fields.Integer,
    'event': fields.String,
    'date': fields.DateTime(dt_format='iso8601')
}
db.create_all()
class Event(Resource):
    @marshal_with(resource_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('start_time')
        parser.add_argument('end_time')
        args = parser.parse_args()
        try:
            if not EventList.query.filter(EventList.date >= datetime.datetime.strptime(args['start_time'], '%Y-%m-%d'),
                                EventList.date <= datetime.datetime.strptime(args['end_time'], '%Y-%m-%d')).all():
                return {"data": "There are no events for that period!"}
            else:
                return EventList.query.filter(EventList.date >= datetime.datetime.strptime(args['start_time'], '%Y-%m-%d'),
                                EventList.date <= datetime.datetime.strptime(args['end_time'], '%Y-%m-%d')).all()
        except TypeError:
            return EventList.query.all()

    def post(self):

        parser.add_argument(
            'event',
            type=str,
            help="The event name is required!",
            required=True
        )
        parser.add_argument(
            'date',
            type=inputs.date,
            help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
            required=True
        )
        args  = parser.parse_args()
        dbinstance = EventList(event=args['event'], date=args['date'])
        # saves data into the table
        db.session.add(dbinstance)
        # commits changes
        db.session.commit()
        return {
            "message": "The event has been added!",
            "event": args['event'],
            "date": args['date'].strftime("%Y-%m-%d")
        }

class Event_today(Resource):
    @marshal_with(resource_fields)
    def get(self):

        if not EventList.query.filter(EventList.date==datetime.date.today()).all():
            return {"data": "There are no events for today!"}
        else :
            return EventList.query.filter(EventList.date==datetime.date.today()).all()
class Event_by_id(Resource):
    @marshal_with(resource_fields)
    def get(self,id):
        event = EventList.query.filter(EventList.id==id).first()
        if event == None :
            abort(404, "The event doesn't exist!")
        return event
    def delete(self, id):
        event = EventList.query.filter(EventList.id==id).first()
        if event == None :
            abort(404, "The event doesn't exist!")
        #tobedeleted=EventList.query.filter_by(id=id).first()
        else:
            db.session.delete(event)
            db.session.commit()
            return {"message":'The event has been deleted!'}

api.add_resource(Event,'/event')
api.add_resource(Event_today,'/event/today')
api.add_resource(Event_by_id,'/event/<int:id>')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
