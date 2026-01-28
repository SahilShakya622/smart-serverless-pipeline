import azure.functions as func

app = func.FunctionApp()

@app.function_name(name="healthcheck")
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS)
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        "Function App is working via GitHub Actions",
        status_code=200
    )