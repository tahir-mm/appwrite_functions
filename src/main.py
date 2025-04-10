from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.exception import AppwriteException
from appwrite.services.databases import Databases
from appwrite.query import Query
import os
import json

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
    users = Users(client)
    databases = Databases(client)
    
    try:
        response = users.list()
        # Log messages and errors to the Appwrite Console
        # These logs won't be seen by your end users
        context.log("Total users: " + str(response["total"]))
        # queries = [{'limit': 100}]
        result = databases.list_documents(
            database_id=os.environ["DATABASE_ID"],
            collection_id=os.environ["COLLECTION_ID"],
            queries=[
                Query.equal("order_status", ["Completed"]),           # WHERE status = 'active'
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
        context.error("Could not list users: " + repr(err))
        return context.res.json({
            "success": False,
            "message": str(err)
        }, status_code=500)

    # The req object contains the request data
    if context.req.path == "/ping":
        # Use res object to respond with text(), json(), or binary()
        # Don't forget to return a response!
        return context.res.text("Pong")

    return context.res.json(
        {
            "motto": "Build like a team of hundreds_",
            "learn": "https://appwrite.io/docs",
            "connect": "https://appwrite.io/discord",
            "getInspired": "https://builtwith.appwrite.io",
        }
    )
