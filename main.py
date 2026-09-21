import pandas as pd
import plotly.express as px
import streamlit as st

# ─────────────────────────────────────────────
# 기본 설정
# ─────────────────────────────────────────────
DATA_URL = (
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
)

st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", page_icon="🎬", layout="wide")


# ─────────────────────────────────────────────
# 데이터 불러오기
# ─────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL, dtype={"영화코드": str})
    # 20240101 같은 여덟 자리 숫자를 진짜 날짜로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df.sort_values("날짜").reset_index(drop=True)


# ─────────────────────────────────────────────
# 공통 도우미: 그래프 아래 '알 수 있는 것' 문구 자리
# ─────────────────────────────────────────────
def show_insight(text: str) -> None:
    st.info(f"💡 **이 그래프로 알 수 있는 것**  \n{text}")


# ─────────────────────────────────────────────
# 구역 1: 영화별 일관객 변화
# ─────────────────────────────────────────────
INSIGHT_1 = "여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요."


def section_1_daily_audience(df: pd.DataFrame) -> None:
    st.header("1. 영화별 일관객 변화")

    # 누적관객이 큰 영화부터 드롭다운에 나오도록 정렬
    movie_order = (
        df.groupby("영화명")["누적관객"].max().sort_values(ascending=False).index.tolist()
    )
    movie = st.selectbox("영화를 골라 보세요", movie_order, key="sec1_movie")

    movie_df = df[df["영화명"] == movie].sort_values("날짜")

    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"{movie} - 날짜별 일관객",
    )
    fig.update_traces(hovertemplate="%{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>")
    fig.update_layout(xaxis_title="날짜", yaxis_title="일관객(명)", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    show_insight(INSIGHT_1)


# ─────────────────────────────────────────────
# 구역 2: 일관객 합계 상위 5편 비교
# ─────────────────────────────────────────────
INSIGHT_2 = "여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요."
TOP_N = 5


def section_2_top5_compare(df: pd.DataFrame) -> None:
    st.header("2. 일관객 합계 상위 5편 비교")

    # 기간 내 일관객 합계가 가장 큰 5편 (합계 큰 순서)
    top_movies = df.groupby("영화명")["일관객"].sum().nlargest(TOP_N).index.tolist()
    top_df = df[df["영화명"].isin(top_movies)].sort_values("날짜")

    fig = px.line(
        top_df,
        x="날짜",
        y="일관객",
        color="영화명",
        category_orders={"영화명": top_movies},  # 범례·색 순서를 합계 순으로 고정
        title="일관객 합계 상위 5편 - 날짜별 일관객",
    )
    fig.update_traces(
        hovertemplate="%{fullData.name}<br>%{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
    )
    fig.update_layout(xaxis_title="날짜", yaxis_title="일관객(명)", hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("범례의 영화명을 클릭하면 그 영화를 끄고 켤 수 있어요. 더블클릭하면 그 영화만 볼 수 있어요.")

    show_insight(INSIGHT_2)


# ─────────────────────────────────────────────
# 구역 3: 날짜별 10위권 일관객 합계 (영역 그래프)
# ─────────────────────────────────────────────
INSIGHT_3 = "여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요."
TOP_DAYS = 3


def section_3_daily_total(df: pd.DataFrame) -> None:
    st.header("3. 날짜별 10위권 일관객 합계")

    # 날짜별로 그날 10위권 일관객을 모두 더함
    daily = df.groupby("날짜", as_index=False)["일관객"].sum()
    top_days = daily.nlargest(TOP_DAYS, "일관객")

    fig = px.area(daily, x="날짜", y="일관객", title="날짜별 10위권 일관객 합계")
    fig.update_traces(hovertemplate="%{x|%Y-%m-%d}<br>합계: %{y:,}명<extra></extra>")

    # 합계가 가장 컸던 3일: 점으로 표시하고 날짜를 적기
    fig.add_scatter(
        x=top_days["날짜"],
        y=top_days["일관객"],
        mode="markers+text",
        text=top_days["날짜"].dt.strftime("%Y-%m-%d"),
        textposition="top center",
        cliponaxis=False,
        marker=dict(size=11, color="red", line=dict(width=1, color="white")),
        name=f"합계 상위 {TOP_DAYS}일",
        hovertemplate="%{x|%Y-%m-%d}<br>합계: %{y:,}명<extra></extra>",
    )
    # 위쪽에 글자가 들어갈 여백 확보
    fig.update_yaxes(range=[0, daily["일관객"].max() * 1.15])
    fig.update_layout(xaxis_title="날짜", yaxis_title="일관객 합계(명)", hovermode="closest")
    st.plotly_chart(fig, use_container_width=True)

    show_insight(INSIGHT_3)


# ─────────────────────────────────────────────
# 구역 4: 일관객 합계 TOP 10 영화 (가로 막대그래프)
# ─────────────────────────────────────────────
INSIGHT_4 = "여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요."
TOP_MOVIES = 10


def section_4_top10_bar(df: pd.DataFrame) -> None:
    st.header("4. 일관객 합계 TOP 10 영화")

    # 영화별 일관객 합계와, 10위권에 든 날수
    summary = (
        df.groupby("영화명")
        .agg(일관객합계=("일관객", "sum"), 십위권일수=("날짜", "nunique"))
        .reset_index()
        .nlargest(TOP_MOVIES, "일관객합계")  # 합계가 큰 순서로 정렬됨
    )

    fig = px.bar(
        summary,
        x="일관객합계",
        y="영화명",
        orientation="h",
        custom_data=["십위권일수"],
        title=f"일관객 합계 TOP {TOP_MOVIES}",
    )
    fig.update_traces(
        hovertemplate=(
            "%{y}<br>일관객 합계: %{x:,}명"
            "<br>10위권에 든 날수: %{customdata[0]}일<extra></extra>"
        )
    )
    # 관객이 많은 영화가 위에 오도록 y축 순서를 뒤집기
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(xaxis_title="일관객 합계(명)", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    show_insight(INSIGHT_4)


# ─────────────────────────────────────────────
# 구역 5: 월 × 요일별 일관객 합계 (히트맵)
# ─────────────────────────────────────────────
INSIGHT_5 = "여기에 이 그래프로 알 수 있는 것을 한 문장으로 적어 주세요."
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]  # 월요일부터 일요일 순서


def section_5_month_weekday_heatmap(df: pd.DataFrame) -> None:
    st.header("5. 월 × 요일별 일관객 합계")

    # 날짜에서 월(1~12)과 요일(0=월요일 ... 6=일요일)을 뽑기
    tmp = df.assign(월=df["날짜"].dt.month, 요일=df["날짜"].dt.dayofweek)
    pivot = (
        tmp.pivot_table(index="월", columns="요일", values="일관객", aggfunc="sum")
        .reindex(columns=range(7))  # 월~일 순서로 고정
        .fillna(0)
    )
    pivot.index = [f"{m}월" for m in pivot.index]
    pivot.columns = WEEKDAYS

    fig = px.imshow(
        pivot,
        color_continuous_scale="Blues",  # 진할수록 관객이 많음
        aspect="auto",
        labels=dict(x="요일", y="월", color="일관객 합계(명)"),
        title="월 × 요일별 일관객 합계",
    )
    fig.update_traces(
        hovertemplate="%{y} %{x}요일<br>일관객 합계: %{z:,.0f}명<extra></extra>"
    )
    fig.update_xaxes(side="top")
    st.plotly_chart(fig, use_container_width=True)

    show_insight(INSIGHT_5)


# ─────────────────────────────────────────────
# 구역 6, 7, ... : 새 그래프는 위와 같은 형태의 함수로 추가하고
# 아래 main()에 한 줄만 넣으면 돼요.
# ─────────────────────────────────────────────


def main() -> None:
    st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
    st.caption("KOBIS 일별 박스오피스 10위권 기록(1년치)으로 시간에 따른 변화를 살펴봐요.")

    df = load_data()

    section_1_daily_audience(df)
    st.divider()

    section_2_top5_compare(df)
    st.divider()

    section_3_daily_total(df)
    st.divider()

    section_4_top10_bar(df)
    st.divider()

    section_5_month_weekday_heatmap(df)
    st.divider()

    # section_6_...(df)
    # st.divider()


if __name__ == "__main__":
    main()
