from .models import (
    Research,
    Tag,
    Reward,
    ResearcheeResearch,
    TagResearch,
    Notice,
    Mark,
    Ask,
    Answer,
)
from .serializers import (
    TagSerializer,
    RewardSerializer,
    SimpleResearchCreateSerializer,
    ResearchCreateSerializer,
    ResearchViewSerializer,
    HotResearchSerializer,
    NewResearchSerializer,
    RecommendResearchSerializer,
    SimpleResearchSerializer,
    NoticeCreateSerializer,
    NoticeSimpleSerializer,
    NoticeDetailSerializer,
    AskCreateSerializer,
    AskSimpleSerializer,
    AskDetailSerializer,
    AnswerSerializer,
)
from .pagination import HomePagination, ListPagination, NoticePagination, AskPagination
from rest_framework.views import APIView, status
from rest_framework.response import Response
from django.http import Http404
from django.db import transaction
from datetime import datetime


class ResearchList(APIView):
    def get(self, request):
        researches = Research.filter(recruit_start__gt=datetime.now())
        page = HomePagination()
        hot_researches = page.paginate_queryset(researches, request)
        hot_serializer = HotResearchSerializer(hot_researches, many=True)
        new_researches = page.paginate_queryset(
            researches.order_by("-create_date"), request
        )
        new_serializer = NewResearchSerializer(new_researches, many=True)
        context = {
            "hot_research": hot_serializer.data,
            "new_research": new_serializer.data,
        }
        return Response(context)

    def post(self, request):
        data = request.data.copy()
        reward = data.pop("reward")
        tags = data.pop("tags")
        serializer = SimpleResearchCreateSerializer(
            data=data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            research = serializer.save(researcher=request.user.profile)

            Reward.objects.create(
                research=research,
                reward_type=reward.get("reward_type"),
                amount=reward.get("amount"),
            )
        for field_tag in tags:
            tag_name = field_tag.get("tag_name")
            try:
                tag = Tag.objects.get(tag_name=tag_name)
            except Tag.DoesNotExist:
                tag_serializer = TagSerializer(data=field_tag)
                tag_serializer.is_valid(raise_exception=True)
                tag = tag_serializer.save()

            with transaction.atomic():
                if TagResearch.objects.filter(research=research, tag=tag).exists():
                    return Response(
                        {"error": "중복된 tag입니다."},
                        status=status.HTTP_409_CONFLICT,
                    )
                TagResearch.objects.create(research=research, tag=tag)
        return Response(
            ResearchCreateSerializer(research).data, status=status.HTTP_201_CREATED
        )


class ResearchDetail(APIView):
    def get_object(self, rid):
        try:
            return Research.objects.get(pk=rid)
        except Research.DoesNotExist:
            raise Http404

    def get(self, request, rid):
        research = self.get_object(rid)
        serializer = ResearchViewSerializer(research)
        return Response(serializer.data)

    def post(self, request, rid):
        research = self.get_object(rid)
        researchee = request.user.researchee
        try:
            already = ResearcheeResearch.objects(
                research=research, researchee=researchee
            )
        except ResearcheeResearch.DoesNotExist:
            ResearcheeResearch.objects.create(research=research, researchee=researchee)
            return Response(status=status.HTTP_201_CREATED)
        return Response({"error": "이미 참여하고 있는 연구입니다."}, status=status.HTTP_409_CONFLICT)

    def put(self, request, rid):
        research = self.get_object(rid)
        data = request.data.copy()
        updated_reward = data.pop("reward")
        updated_tags = data.pop("tags")

        try:
            reward = Reward.objects.filter(research=research)
            serializer = RewardSerializer(reward, data=updated_reward)
            serializer.is_valid(raise_exception=True)
            reward = serializer.save()
        except Reward.DoesNotExist:
            serializer = RewardSerializer(data=reward)
            serializer.is_valid(raise_exception=True)
            reward = serializer.save()

        old_tags = TagResearch.objects.filter(research=research)
        for updated_tag in updated_tags:
            tag_name = updated_tag.get("tag_name")
            try:
                tag = Tag.objects.get(tag_name=tag_name)
            except Tag.DoesNotExist:
                tag = Tag.objects.create(tag_name=tag_name)

            if old_tags.filter(tag__tag_name=tag_name).exists():
                old_tags.exclude(tag__tag_name=tag_name)
            else:
                TagResearch.objects.create(research=research, tag=tag)
        for old_tag in old_tags:
            old_tag.delete()

        return Response(
            ResearchCreateSerializer(research).data, status=status.HTTP_200_OK
        )

    def delete(self, request, rid):
        research = self.get_object(rid)
        research.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NoticeList(APIView):
    def get(self, request, rid):
        notices = Notice.objects.filter(research__id=rid)
        page = NoticePagination()
        notices = page.paginate_queryset(notices, request)
        serializer = NoticeSimpleSerializer(notices, many=True)
        return Response(serializer.data)

    def post(self, request, rid):
        serializer = NoticeCreateSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        research = Research.objects.get(id=rid)
        if serializer.is_valid():
            serializer.save(research=research)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NoticeDetail(APIView):
    def get_object(self, nid):
        try:
            return Notice.objects.get(pk=nid)
        except Research.DoesNotExist:
            raise Http404

    def get(self, request, rid, nid):
        notice = self.get_object(nid)
        serializer = NoticeDetailSerializer(notice)
        return Response(serializer.data)

    def delete(self, request, rid, nid):
        notice = self.get_object(nid)
        notice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AskList(APIView):
    def get(self, request, rid):
        asks = Ask.objects.filter(research__id=rid)
        page = AskPagination()
        asks = page.paginate_queryset(asks, request)
        serializer = AskSimpleSerializer(asks, many=True)
        return Response(serializer.data)

    def post(self, request, rid):
        serializer = AskCreateSerializer(
            request.data, context=self.get_serializer_context()
        )
        research = Research.objects.get(id=rid)
        asker = request.user.profile
        if serializer.is_valid():
            serializer.save(research=research, asker=asker)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AskDetail(APIView):
    def get_object(self, aid):
        try:
            return Ask.objects.get(pk=aid)
        except Research.DoesNotExist:
            raise Http404

    def get(self, request, rid, aid):
        ask = self.get_object(aid)
        serializer = AskDetailSerializer(ask)
        return Response(serializer.data)

    def delete(self, request, rid, aid):
        ask = Ask.objects.get(pk=aid)
        ask.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SearchList(APIView):
    def get(self, request):
        keyword = request.query_params.get("query")
        sort = request.query_params.get("sort")
        pay = request.query_params.get("pay")
        time_range = request.query_params.get("time_range")
        page = ListPagination()

        search_result = Research.objects.filter(subject__iexact=keyword)
        if sort:
            search_result = search_result.order_by(sort)
        if pay:
            search_result = search_result.filter(reward__amount__gte=pay)
        if time_range:
            start = datetime(time_range[0], time_range[1], time_range[2], 0, 0)
            end = datetime(time_range[3], time_range[4], time_range[5], 0, 0)
            search_result = search_result.filter(research_start__range=(start, end))
            search_result = search_result.filter(research_end__range=(start, end))
        search_result = page.paginate_queryset(search_result, request)
        serializer = SimpleResearchSerializer(search_result, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FieldList(APIView):
    def get(self, request):
        tags = request.query_params.get("tags")
        sort = request.query_params.get("sort")
        pay = request.query_params.get("pay")
        time_range = request.query_params.get("time_range")
        page = ListPagination()

        filter_result = Research.objects.filter(tags__tag_name__in=tags)

        if sort:
            filter_result = filter_result.order_by(sort)
        if pay:
            filter_result = filter_result.filter(reward__amount__gte=pay)
        if time_range:
            start = datetime(time_range[0], time_range[1], time_range[2], 0, 0)
            end = datetime(time_range[3], time_range[4], time_range[5], 0, 0)
            filter_result = filter_result.filter(research_start__range=(start, end))
            filter_result = filter_result.filter(research_end__range=(start, end))
        filter_result = page.paginate_queryset(filter_result, request)
        serializer = SimpleResearchSerializer(filter_result, many=True)


class RecommendList(APIView):
    def get(self, request):
        interests = request.user.researchee.interests
        sort = request.query_params.get("sort")
        page = ListPagination()
        recommendations = Research.obejects.filter(
            tags__tag_name__in=interests
        ).order_by(sort)
        recommendations = page.paginate_queryset(recommendations, request)
        serializer = RecommendResearchSerializer(recommendations, many=True)
        return Response(serializer.data)
