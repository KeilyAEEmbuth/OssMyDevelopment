from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import graphviz as graphviz

st.title("📍 컨퍼런스 부스 안내")

st.title ("this is the app title")
st.header("this is the markdown")
st.markdown("this is the header")
st.subheader("this is the subheader")
st.caption("this is the caption")
st.code("x=2021")
st.latex(r''' a+a r^1+a r^2+a r^3 ''')

st.markdown("---")

st.image("kid.jpg")
st.audio("audio.ogg")
st.video("video.mp4")

st.markdown("---")

st.checkbox('yes')
st.button('Click')
st.radio('Pick your gender',['Male','Female'])
st.selectbox('Pick your gender',['Male','Female'])
st.multiselect('choose a planet',['Jupiter', 'Mars', 'neptune'])
st.select_slider('Pick a mark', ['Bad', 'Good', 'Excellent'])
st.slider('Pick a number', 0,50)

st.markdown("---")

st.number_input('Pick a number', 0,10)
st.text_input('Email address')
st.markdown("this is the header")
st.date_input('Travelling date')
st.time_input('School time')
st.text_area('Description')
st.file_uploader('Upload a photo')
st.color_picker('Choose your favorite color')

st.markdown("---")

rand=np.random.normal(1, 2, size=20)
fig, ax = plt.subplots()
ax.hist(rand, bins=15)
st.pyplot(fig)

st.markdown("---")

df= pd.DataFrame(np.random.randn(10, 2),columns=['x', 'y'])
st.line_chart(df)

st.markdown("---")

st.graphviz_chart('''    
	digraph {        
		Big_shark -> Tuna       
		Tuna -> Mackerel        
		Mackerel -> Small_fishes        
		Small_fishes -> Shrimp    
}
''')

st.markdown("---")

df = pd.DataFrame(np.random.randn(500, 2) / [50, 50] + [37.76, -122.4],columns=['lat', 'lon'])
st.map(df)

st.markdown("---")

# 부스 선택 버튼
selected_booth = st.radio(
    "부스를 선택해주세요:",
    ["A관 - AI 체험존", "B관 - 스타트업 홍보부스", "C관 - 휴게/푸드존"]
)

# 각 부스에 대한 이미지와 설명을 조건 분기
if selected_booth == "A관 - AI 체험존":
    st.image("booth_a_overview.png", caption="A관 위치도")
    st.image("booth_a_inside.jpg", caption="AI 체험존 내부 모습")
    st.markdown("""
    **A관 - AI 체험존**  
    ChatGPT, 이미지 생성 AI, 음성 합성 기술 등을 체험할 수 있습니다.  
    위치: 본관 1층 중앙홀
    """)

elif selected_booth == "B관 - 스타트업 홍보부스":
    st.image("booth_b_overview.png", caption="B관 위치도")
    st.image("booth_b_inside.jpg", caption="스타트업 부스 모습")
    st.markdown("""
    **B관 - 스타트업 홍보부스**  
    혁신 기술을 보유한 스타트업들의 제품 시연 및 IR 부스입니다.  
    위치: 본관 2층 로비
    """)

elif selected_booth == "C관 - 휴게/푸드존":
    st.image("booth_c_overview.png", caption="C관 위치도")
    st.image("booth_c_inside.jpg", caption="푸드존 전경")
    st.markdown("""
    **C관 - 푸드 & 휴게존**  
    간식, 음료, 휴식 공간이 마련되어 있습니다.  
    위치: 별관 1층 뒤편
    """)
