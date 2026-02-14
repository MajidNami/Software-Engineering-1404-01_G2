from externalServices.grpc.client.Clients import Clients
from infrastructure.grpc_clients import trip_pb2 as pb2


class TripPlanService:

    def create_trip(self,destination):
        client=Clients.get_trip_plan_client()
        create_response = client.CreateTrip(pb2.CreateTripRequest(destination=destination))
        print("Created Trip:", create_response)

        list_response = client.ListTrips(pb2.Empty())
        print("All Trips:")
        for trip in list_response.trips:
            print(f"{trip.id} -> {trip.destination}")