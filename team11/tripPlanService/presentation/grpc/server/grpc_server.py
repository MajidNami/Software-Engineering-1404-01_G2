import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "tripPlanService.settings"
)

django.setup()
from presentation.grpc.services.TripServicer import TripServicer
import grpc
from concurrent import futures

from infrastructure.grpc_clients import trip_pb2_grpc as pb2_grpc




def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_TripServiceServicer_to_server(TripServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC running on port 50051...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
