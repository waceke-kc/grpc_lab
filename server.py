import grpc
#add grpc_reflection
from grpc_reflection.v1alpha import reflection
from concurrent import futures
import myitems_pb2 as pb2
import myitems_pb2_grpc as pb2_grpc

items = [
    {"id": 1, "name": "First"},
    {"id": 2, "name": "Second"}
]

class ItemServiceServicer(pb2_grpc.ItemServiceServicer):
    #Unary
    def GetItemById(self, request, context):   
        for item in items:
            if item["id"] == request.id: 
               return pb2.ItemResponse(id=item["id"], name = item["name"])
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details(f"Item with id {request.id} not found")
        return pb2_grpc.ItemResponse()

    # Server Streaming
    def ListAllItems(self, request, context):
       for item in items: 
          yield pb2.ItemResponse(id=item["id"], name = item["name"])

    # Client Streaming
    def AddItems(self, request_iterator, context): 
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
        return pb2.ItemsCount(total_count = count)
    # Bidirectional Streaming
    def ChatAboutItems(self, request_iterator, context):
        for message in request_iterator:
           reply= f"Your message was: { message.content}"
           yield pb2.ChatMessage(content=reply)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ItemServiceServicer_to_server(
        ItemServiceServicer(),
        server
    )
    # Enable reflection
    # The reflection service will be aware of all services in the server.
    SERVICE_NAMES = (
        pb2.DESCRIPTOR.services_by_name['ItemService'].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(SERVICE_NAMES, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
 serve()