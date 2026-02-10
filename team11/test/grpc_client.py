import grpc

from team11.test.protos import trip_pb2 as pb2
from protos import trip_pb2_grpc as pb2_grpc


def run():
    channel = grpc.insecure_channel("localhost:9151/grpc/")
    stub = pb2_grpc.TripServiceStub(channel)

    destination = "Paris"
    create_response = stub.CreateTrip(
        pb2.CreateTripRequest(destination=destination)
    )
    print("Created Trip:", create_response)

    list_response = stub.ListTrips(pb2.Empty())
    print("All Trips:")
    for trip in list_response.trips:
        print(f"{trip.id} -> {trip.destination}")


if __name__ == "__main__":
    run()
