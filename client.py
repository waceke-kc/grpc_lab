import grpc
import myitems_pb2 as pb2
import myitems_pb2_grpc as pb2_grpc


def run():
    channel = grpc.insecure_channel("localhost:50051", options=(('grpc.enable_http_proxy', 0),))
    stub = pb2_grpc.ItemServiceStub(channel)
    # 1. Unary call

    response = stub.GetItemById(pb2.ItemRequest(id=1))
    print("Unary response:", response)

    # 2. Server-streaming
    # items = stub.ListAllItems(pb2.Empty())
    # Call stub.ListAllItems() and print the responses
    for item in stub.ListAllItems(pb2.Empty()):
        print("Server-streaming item:", item)

    names = ["Moodle", "Student Services", "WebUntis", " Student Mail"]

    def name_generator():
        for name in names:
            yield pb2.ItemName(name=name)
    # 3. Client-streaming
    # Create an iterator of ItemRequest messages
    # Then call stub.AddItems(...) and capture the final result
    response = stub.AddItems(name_generator())
    print("Client-streaming response. The new items count is:", response.total_count)

    # 4. Bidirectional
    # Open a stub.ChatAboutItems() stream
    # Send ChatMessage objects and read responses in a loop
    def chat_generator():
        for name in names:
            print("Sending chat message:", name)
            # Create a ChatMessage object and send it
            yield pb2.ChatMessage(content=f"Hello from {name}")
    # Call stub.ChatAboutItems() and print the responses
    response = stub.ChatAboutItems(chat_generator())
    for message in response:
        print("Bidirectional response:", message.content)
    # 5. Error handling


if __name__ == "__main__":
    run()
