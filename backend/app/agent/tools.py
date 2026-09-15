"""
Owner: Member 4 (AI / Agent Engineer)
Defines the ONE tool the agent has for getting numbers: query_semantic_layer.
"""
from langchain.tools import StructuredTool
from pydantic import BaseModel, Field

from app.semantic_client import cube_client

SEMANTIC_SCHEMA_SUMMARY = """
Cube: Sales
Measures:
  - Sales.revenue        (sum of governed revenue)
  - Sales.materialCost   (sum of material cost)
  - Sales.shippingCost   (sum of shipping cost)
  - Sales.totalCost      (sum of total cost)
  - Sales.margin         (revenue - total cost)
  - Sales.marginPct      (margin / revenue, weighted — never average it yourself)
Dimensions:
  - Sales.orderDate (time)
  - Sales.quarter   ("Q1" | "Q2" | "Q3")
  - Sales.region    ("Europe" | "North America" | "APAC")
  - Sales.country
  - Sales.productName
  - Sales.category
"""


class SemanticQueryInput(BaseModel):
    measures: list[str] = Field(..., description="e.g. ['Sales.revenue','Sales.margin']")
    dimensions: list[str] = Field(default_factory=list, description="e.g. ['Sales.region']")
    filters: list[dict] = Field(
        default_factory=list,
        description=(
            "Cube.dev filter objects, e.g. "
            "{'member':'Sales.region','operator':'equals','values':['Europe']}"
        ),
    )
    time_dimensions: list[dict] = Field(
        default_factory=list,
        description="e.g. [{'dimension':'Sales.orderDate','granularity':'quarter'}]",
    )


def _query_semantic_layer(measures, dimensions=None, filters=None, time_dimensions=None):
    return cube_client.run_query(
        measures=measures,
        dimensions=dimensions,
        filters=filters,
        time_dimensions=time_dimensions,
    )


query_semantic_layer_tool = StructuredTool.from_function(
    func=_query_semantic_layer,
    name="query_semantic_layer",
    description=(
        "The ONLY way to get real numbers. Never write SQL. Pass governed "
        "measure/dimension names exactly as listed in the schema you were "
        "given. Returns {query, generated_sql, data} — data is a list of rows."
    ),
    args_schema=SemanticQueryInput,
)