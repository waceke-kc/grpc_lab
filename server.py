import grpc
#add grpc_reflection
from grpc_reflection.v1alpha import reflection
from concurrent import futures
import myitems_pb2 as pb2
import myitems_pb2_grpc as pb2_grpc
import time
import logging

# Configurations for better code readability
ENABLE_LOGGING_INTERCEPTOR = False
ENABLE_REFLECTION = False

items = [
    {"id": 1, "name": "First"},
    {"id": 2, "name": "Second"}
]

## use logging instead of print
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ItemServiceServicer(pb2_grpc.ItemServiceServicer):
    #Unary
    def GetItemById(self, request, context):   
        logging.info(f"*** GetItemById called for id: {request.id}\n")
        for item in items:
            if item["id"] == request.id: 
               return pb2.ItemResponse(id=item["id"], name = item["name"])
        context.set_code(grpc.StatusCode.NOT_FOUND)
        logging.error(f"Item with id {request.id} not found")
        context.set_details(f"Item with id {request.id} not found")
        return pb2_grpc.ItemResponse()

    # Server Streaming
    def ListAllItems(self, request, context):
       logging.info("*** ListAllItems called\n")
       for item in items: 
          yield pb2.ItemResponse(id=item["id"], name = item["name"])

    # Client Streaming
    def AddItems(self, request_iterator, context): 
        logging.info("*** AddItems called\n")
        count = len(items)
        if len(items)> 0 :
            last_id = items[-1]['id'] 
        else:
            last_id = 0
        for item in request_iterator:
            new_item =  { 'id': last_id+1, 'name': item.name}
            items.append(new_item)
            last_id += 1
            count += 1
            logging.info(f"New item added. Total count is now: {count}")
        return pb2.ItemsCount(total_count = count)
    # Bidirectional Streaming
    def ChatAboutItems(self, request_iterator, context):
        for message in request_iterator:
           reply= f"Your message was: { message.content}"
           yield pb2.ChatMessage(content=reply)

class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        metadata = handler_call_details.invocation_metadata
        logging.info(f"[gRPC LOG] Method: {method}, Metadata: {metadata}")
        return continuation(handler_call_details) # meaning gRPC can be continued

def serve():
    interceptors = [LoggingInterceptor()] if ENABLE_LOGGING_INTERCEPTOR else []
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=interceptors
    )

    logging.info("Starting gRPC server...")
    pb2_grpc.add_ItemServiceServicer_to_server(
        ItemServiceServicer(),
        server
    )
    if ENABLE_REFLECTION:
        logging.info("Enabling gRPC reflection...")
        SERVICE_NAMES = (
            pb2.DESCRIPTOR.services_by_name['ItemService'].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
   
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info(f"*** gRPC server started with default items loaded. Listening on port 50051\n")
    server.wait_for_termination()

if __name__ == '__main__':
 serve()