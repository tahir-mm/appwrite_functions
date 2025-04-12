from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases
from appwrite.query import Query
import os
import json

#Function to get all users number
def getAllUsers(context, client):
    print("in getting database users:")
    users = Users(client)
    try:
        response = users.list()
        # Log messages and errors to the Appwrite Console
        # These logs won't be seen by your end users
        context.log("Total users: " + str(response["total"]))
        return context.res.json({
            "success": True,
            "message": "Documents fetched successfully.",
            "documents": response["total"]
        })
    except AppwriteException as err:
        context.error("Could not list users: " + repr(err))
        return context.res.json({
            "success": False,
            "message": str(err)
        }, status_code=500)    


#Function to test ping/pong
def pingPong(context):
    return context.res.text("Pong")

def getAllOrders(context, databases, status):
    try:
        context.log("Getting all " + status + " orders: ")
        result = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["ORDER_COLLECTION_ID"],
            queries=[
                Query.equal("order_status", [status]),           # WHERE status = 'active'
                Query.select(["order_no", "grand_total", "order_date", "order_status", "userTbl.full_name", "userTbl.mobile"]),
                Query.limit(500)              # ORDER BY createdAt DESC
            ]
        )
        context.log("Total Orders: " + str(result["documents"]))
        return context.res.json({
            "success": True,
            "message": "Documents fetched successfully.",
            "documents": str(result["documents"])
        })
    except AppwriteException as err:
        context.error("Could not list Orders: " + repr(err))
        return context.res.json({
            "success": False,
            "message": str(err)
        }, status_code=500)        

# Order with item 
def getOrderByNumber(context, databases, number):
    try:
        context.log("Getting " + number + " order: ")
        result = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["ORDER_COLLECTION_ID"],
            queries=[
                Query.equal("order_no", [number]),           # WHERE status = 'active'
                Query.select(["order_no", "grand_total", "order_date", "order_status", "userTbl.full_name", "userTbl.mobile"]),
                Query.limit(5)              # ORDER BY createdAt DESC
            ]
        )
        context.log("Total Orders: " + str(result["documents"]))
        return context.res.json({
            "success": True,
            "message": "Documents fetched successfully.",
            "documents": str(result["documents"])
        })
    except AppwriteException as err:
        context.error("Could not list Orders: " + repr(err))
        return context.res.json({
            "success": False,
            "message": str(err)
        }, status_code=500) 
    
def getAllOrderTotalByStatus(context, databases, status):
    try:
        context.log("Getting total of " + status + " orders")
        result = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["ORDER_COLLECTION_ID"],
            queries=[
                Query.equal("order_status", [status]),           # WHERE status = 'active'
                Query.select(["order_no", "grand_total", "order_status"]),
                Query.limit(500)              # ORDER BY createdAt DESC
            ]
        )
        context.log("Total Orders: " + str(result["documents"]))
        sum_of_orders = 0
        for order in result["documents"]:
            sum_of_orders += order["grand_total"]

        return context.res.json({
            "success": True,
            "message": "Documents fetched successfully.",
            "documents": result["documents"],
            "sum": sum_of_orders
        })
    except AppwriteException as err:
        context.error("Could not list Orders: " + repr(err))
        return context.res.json({
            "success": False,
            "message": str(err)
        }, status_code=500) 

def getAllProduct(context, databases, quantity):
    try:
        # Log messages and errors to the Appwrite Console
        # These logs won't be seen by your end users
        context.log("Getting all product with quantity ["+quantity+"]: ")
        result = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["PRODUCT_COLLECTION_ID"],
            queries=[
                Query.lessThan("available_quantity", quantity),
                Query.select(["$id", "title", "summary", "price", "listed_quantity", "available_quantity", "thumbnail"]),
                Query.limit(20)                
              # ORDER BY createdAt DESC
            ]
        )
        context.log("Total Products: " + str(result["documents"]))
        return context.res.json({
            "success": True,
            "message": "Documents fetched successfully.",
            "documents": str(result["documents"])
        })
    except AppwriteException as err:
        context.error("Could not list Product: " + repr(err))
        return context.res.json({
            "success": False,
            "message": str(err)
        }, status_code=500)     

# This Appwrite function will be executed every time your function is triggered
def main(context):
    # You can use the Appwrite SDK to interact with other services
    # For this example, we're using the Users service
    client = (
        Client()
        .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])
        .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])
        .set_key(context.req.headers["x-appwrite-key"])
    )
    databases = Databases(client)
    # The req object contains the request data
    # Use res object to respond with text(), json(), or binary()
    # Don't forget to return a response!    
    if context.req.path == "/ping":
        return pingPong(context)
    elif context.req.path == "/users":  
        return getAllUsers(context, client)  
    elif "/products/" in context.req.path :  
        tokens = context.req.path.split("/")
        return getAllProduct(context, databases, tokens[len(tokens) - 1])  
    elif "/order/" in context.req.path:  #"/order/{status}"
        tokens = context.req.path.split("/")
        context.log("Orders by order statys: ", len(tokens), str(tokens))
        return getAllOrders(context, databases, tokens[len(tokens) - 1])     
    elif "/orderDetail" in context.req.path:  #"/orderDetail/{order_no}"
        tokens = context.req.path.split("/")
        return getOrderByNumber(context, databases, tokens[len(tokens) - 1])              
    elif context.req.path == "/orderTotal/Completed":  #"/orderTotal/Completed"
        tokens = context.req.path.split("/")
        return getAllOrderTotalByStatus(context, databases, tokens[len(tokens) - 1])     
    else:        
        return context.res.json(
            {
                "motto": "Build like a team of hundreds_",
                "learn": "https://appwrite.io/docs",
                "connect": "https://appwrite.io/discord",
                "getInspired": "https://builtwith.appwrite.io",
            }
        )


