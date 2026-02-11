import os

from infrastructure.grpc_clients import trip_pb2 as pb2
from infrastructure.grpc_clients import trip_pb2_grpc as pb2_grpc
from business.services import TripService
from externalServices.rest.TripPlanClient import TripPlanClient

class TripServicer(pb2_grpc.TripServiceServicer):

    def CreateTrip(self, request, context):
        trip = TripService.create_trip(request.destination)
        return pb2.TripResponse(
            id=str(trip.id),
            destination=trip.destination
        )

    def ListTrips(self, request, context):
        trips = TripService.get_trips()
        return pb2.TripListResponse(
            trips=[
                pb2.Trip(id=str(t.id), destination=t.destination)
                for t in trips
            ]
        )
