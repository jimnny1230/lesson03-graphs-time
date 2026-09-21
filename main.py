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
# 구역 2, 3, ... : 새 그래프는 위와 같은 형태의 함수로 추가하고
# 아래 main()에 한 줄만 넣으면 돼요.
# ─────────────────────────────────────────────


def main() -> None:
    st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
    st.caption("KOBIS 일별 박스오피스 10위권 기록(1년치)으로 시간에 따른 변화를 살펴봐요.")

    df = load_data()

    section_1_daily_audience(df)
    st.divider()

    # section_2_...(df)
    # st.divider()


if __name__ == "__main__":
    main()
