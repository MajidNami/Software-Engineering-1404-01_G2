import os

from infrastructure.grpc_clients import trip_pb2_grpc as pb2_grpc
from infrastructure.grpc_clients import facility_pb2_grpc as facility
from infrastructure.grpc_clients import wiki_pb2_grpc as wiki
from infrastructure.grpc_clients import recom_pb2_grpc as recom


import grpc

TRIP_PLAN_GRPC_URL = os.getenv("TRIP_PLAN_GRPC_URL", "localhost:59007")
FACILITY_GRPC_URL = os.getenv("FACILITY_GRPC_URL", "localhost:59007")
WIKI_PLAN_GRPC_URL = os.getenv("WIKI_PLAN_GRPC_URL", "localhost:59007")
RECOM_GRPC_URL = os.getenv("RECOM_GRPC_URL", "localhost:59007")


class Clients:

    @staticmethod
    def get_trip_plan_client():
        channel = grpc.insecure_channel(TRIP_PLAN_GRPC_URL)
        stub = pb2_grpc.TripServiceStub(channel)
        return stub

    @staticmethod
    def get_facility_client():
        channel = grpc.insecure_channel(FACILITY_GRPC_URL)
        stub = facility.FacilityServiceStub(channel)
        return stub

    @staticmethod
    def get_wiki_client():
        channel = grpc.insecure_channel(WIKI_PLAN_GRPC_URL)
        stub = wiki.WikiServiceStub(channel)
        return stub

    @staticmethod
    def get_recom_client():
        channel = grpc.insecure_channel(RECOM_GRPC_URL)
        stub = recom.RecommendationServiceStub(channel)
        return stub

