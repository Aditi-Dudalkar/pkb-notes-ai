import strawberry

@strawberry.type
class Query:
    hello: str = "Hello from GraphQL!"

schema = strawberry.Schema(query=Query)
