from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.id import ID
from datetime import datetime, timedelta

import os
import json

#Function to get all users number
def getAllUsers(context, client):
    context.log("in getting database users:")
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
        context.log("Total Orders: " + str(len(result["documents"])))
        context.log(str(result["documents"]))
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
def getItemSales(context, databases, id):
    try:
        context.log("Getting all sales against Item :  " + id )
        orderItems = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["ORDER_ITEM_COLLECTION_ID"],
            queries=[
                Query.equal('productTbl', [id]),
                Query.select(["$id", "$createdAt", "order_quantity", "unit_price", "price", "orderTbl.order_no"]),  
                Query.limit(500)              # ORDER BY createdAt DESC
            ]
        )
        context.log("Total Item Sale : " + str(len(orderItems["documents"])))
        context.log(str(orderItems["documents"]))
        
        return context.res.json({
            "success": True,
            "message": "Documents fetched successfully.",
            "documents": str(orderItems["documents"])
        })
    except AppwriteException as err:
        context.error("Could not list item sale: " + repr(err))
        return context.res.json({
            "success": False,
            "message": str(err)
        }, status_code=500) 


# Order with item 
def getOrderByNumber(context, databases, number):
    try:
        context.log("Getting order number " + number + ": ")
        orders = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["ORDER_COLLECTION_ID"],
            queries=[
                Query.equal("order_no", [int(number)]),           # WHERE status = 'active'
                Query.select(["$id", "order_no", "grand_total", "order_date", "order_status", "userTbl.full_name", "userTbl.mobile"])
            ]
        )
        context.log("Order: " + str(orders["documents"]))
        if len(orders["documents"]) > 0 :
            order = orders["documents"][0]
            orderItems = databases.list_documents(
                database_id=os.environ["DATABASE_ID"],
                collection_id=os.environ["ORDER_ITEM_COLLECTION_ID"],
                queries=[
                    Query.equal('orderTbl', order["$id"]),
                    Query.select(["$id", "order_quantity", "unit_price", "price", "productTbl.title", "productTbl.summary"]),  
                    Query.limit(500)              # ORDER BY createdAt DESC
                ]
            )
            context.log("Order Details : " + str(orderItems["documents"]))
        else:
            context.log("Not found!")


        return context.res.json({
            "success": True,
            "message": "Documents fetched successfully.",
            "documents": str(orderItems["documents"])
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
        
        sum_of_orders = 0
        for order in result["documents"]:
            sum_of_orders += order["grand_total"]
        
        context.log("Total Orders: " + str(len(result["documents"])))
        context.log(" -- GRAND TOTAL --" + str(sum_of_orders))
        context.log(str(result["documents"]))

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




def prepareItemSaleSummary(context, databases):
    try:
        context.log("Getting all Item sales count :  ")
        current_datetime = datetime.utcnow()
        seven_days_ago = current_datetime - timedelta(days=7)
        context.log("Current DateTime", current_datetime)
        context.log("7 Days ago DateTime", seven_days_ago)

        orderItems = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["ORDER_ITEM_COLLECTION_ID"],
            queries=[
                Query.greater_than("$createdAt", [str(seven_days_ago)]),
                Query.less_than_equal("$createdAt", [str(current_datetime)]),
                Query.select(["$id", "$createdAt", "order_quantity", "unit_price", "price", "productTbl.title"]),  
                Query.limit(10)              # ORDER BY createdAt DESC
            ]
        )
        context.log("Total Item Sale : " + str(len(orderItems["documents"])))
        context.log(str(orderItems["documents"]))

        data_map = {}
        for item in orderItems["documents"]:
            data_map[item.productTbl.title] = {item.order_quantity, item.unit_price, item.price}

        
        for key, value in data_map.items():
            context.log(str(key) + ' - ' + str(value))


        return context.res.json({
            "success": True,
            "message": "Documents fetched successfully.",
            "documents": str(orderItems["documents"])
        })
    except AppwriteException as err:
        context.error("Could not list item sale: " + repr(err))
        return context.res.json({
            "success": False,
            "message": str(err)
        }, status_code=500) 




def getAllProduct(context, databases, quantity):
    try:
        # Log messages and errors to the Appwrite Console
        # These logs won't be seen by your end users
        context.log("Getting all product with quantity ["+quantity+"] or less: ")
        result = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["PRODUCT_COLLECTION_ID"],
            queries=[
                Query.less_than_equal("available_quantity", [int(quantity)]),
                Query.select(["$id", "title", "summary", "price", "listed_quantity", "available_quantity", "thumbnail"]),
                Query.limit(5000)                
              # ORDER BY createdAt DESC
            ]
        )
        context.log("Total Products: " + str(len(result["documents"])))
        context.log(str(result["documents"]))
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
        # .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])
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
    elif "/orderTotal" in context.req.path:  #"/orderTotal/Completed"
        tokens = context.req.path.split("/")
        return getAllOrderTotalByStatus(context, databases, tokens[len(tokens) - 1]) 
    elif "/itemSale" in context.req.path:  #"/itemSale/{productId}"
        tokens = context.req.path.split("/")
        return getItemSales (context, databases, tokens[len(tokens) - 1])      
    elif "/itemSummary" in context.req.path:  #"/orderTotal/Completed"
        return prepareItemSaleSummary (context, databases)           
    else:        
        return context.res.json(
            {
                "motto": "Build like a team of hundreds_",
                "learn": "https://appwrite.io/docs",
                "connect": "https://appwrite.io/discord",
                "getInspired": "https://builtwith.appwrite.io",
            }
        )


