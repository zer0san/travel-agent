import asyncio

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import os
import dotenv
from app.model.TripPlan import TripPlan
from app.model.TripPlanRequest import TripPlanRequest
from app.model.Weather import Weather
from app.model.Hotel import Hotel
from app.model.Attraction import Attraction
from app.service.mcp_service import get_mcp_tools

ATTRACTION_AGENT_PROMPT = """
你是一个旅游景点搜索专家。你必须使用工具搜索景点信息，不要编造。
"""

WEATHER_AGENT_PROMPT = """
你是一个天气预报专家。你必须使用工具搜索天气信息，不要编造。
"""

HOTEL_AGENT_PROMPT = """
你是酒店推荐专家，请使用工具搜索酒店信息，不要编造数据。
"""

PLANNER_AGENT_PROMPT = """
你是一个旅游行程规划专家，你将根据旅游景点搜索专家、天气预报专家、酒店推荐专家返回的内容，生成一个旅游行程规划。
规划要求：
- 考虑每天的天气、气温、风力等天气因素
- 每天安排适当数量的景点
- 包含早中晚三餐
- 提供实用建议
- 包含预算信息(景点门票、餐饮、住宿、交通等费用)
"""

_planner_agent = None


async def get_planner_agent():
    global _planner_agent
    if _planner_agent is None:
        _planner_agent = await MultiAgent.create()

    return _planner_agent


class MultiAgent:
    def __init__(self, gaode_tools):
        weather_model = ChatOpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL_NAME")
        )

        attraction_model = ChatOpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL_NAME")
        )

        hotel_model = ChatOpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL_NAME")
        )

        planner_model = ChatOpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            model=os.getenv("LLM_MODEL_NAME")
        )

        self.weather_agent = create_agent(
            model=weather_model,
            system_prompt=WEATHER_AGENT_PROMPT,
            tools= gaode_tools,
            response_format=Weather
        )

        self.attraction_agent = create_agent(
            model=attraction_model,
            system_prompt=ATTRACTION_AGENT_PROMPT,
            tools=gaode_tools,
            response_format=Attraction
        )

        self.hotel_agent = create_agent(
            model=hotel_model,
            system_prompt=HOTEL_AGENT_PROMPT,
            tools= gaode_tools,
            response_format=Hotel
        )

        self.planner_agent = create_agent(
            model=planner_model,
            system_prompt=PLANNER_AGENT_PROMPT,
            tools= [],
            response_format=TripPlan
        )

    @classmethod
    async def create(cls):
        dotenv.load_dotenv()
        gaode_tools = await get_mcp_tools()
        return cls(gaode_tools)

    @staticmethod
    def _extract_response(agent_result):
        if isinstance(agent_result, dict):
            structured = agent_result.get("structured_response")
            if structured is not None:
                return structured

            messages = agent_result.get("messages") or []
            if messages:
                last_message = messages[-1]
                return getattr(last_message, "content", last_message)

        return agent_result

    # @tool
    async def plan_trip(self, request: TripPlanRequest)->TripPlan:
        '''the planner agent plan the trip, based on the request and the information provided by other agents'''
        weather_msg = f"帮我查询{request.city}城市的天气。"

        # search the attraction
        attraction_msg = f'请提供{request.city}城市，具有{request.preferences}特点的景点。'
        if request.additional_request is not None:
            attraction_msg = attraction_msg + f"额外要求: {request.additional_request}。"


        # search the hotel\
        hotel_msg = f'请提供{request.city}城市的酒店。'
        if request.accommodation is not None:
            hotel_msg = hotel_msg + f'最好符合{request.accommodation}的要求'


        # wait for the result
        weather_result, attraction_result, hotel_result = await asyncio.gather(
            self.weather_agent.ainvoke({"messages":[HumanMessage(weather_msg)]}),  # type: ignore[arg-type]
            self.attraction_agent.ainvoke({"messages":[HumanMessage(attraction_msg)]}),  # type: ignore[arg-type]
            self.hotel_agent.ainvoke({"messages":[HumanMessage(hotel_msg)]})  # type: ignore[arg-type]
        )

        weather_res = self._extract_response(weather_result)
        attraction_res = self._extract_response(attraction_result)
        hotel_res = self._extract_response(hotel_result)

        # generate the trip plan

        planner_msg = f'请根据以下信息，生成一个旅游行程规划：\n天气信息：{weather_res}\n景点信息：{attraction_res}\n酒店信息：{hotel_res}'
        planner_result = await self.planner_agent.ainvoke({"messages":[HumanMessage(planner_msg)]})  # type: ignore[arg-type]
        return self._extract_response(planner_result)

