import streamlit as st

st.set_page_config(page_title="대봉 업무 시스템", page_icon="🏭", layout="wide")

st.markdown("""
# 🏭 대봉 업무 시스템

업무를 가볍게 쓰기 위해 앱을 2개로 분리했습니다.

- **ERP 앱**: 거래처, 출고일지, 기사, 경비 관리
- **견적서 앱**: 견적 작성, 저장된 견적서, PDF 출력

왼쪽 터미널/서버에서 아래 명령으로 각각 실행하세요.

```bash
streamlit run erp_app.py --server.port 8501
streamlit run quote_app.py --server.port 8502
```

두 앱은 같은 `database/` 폴더의 JSON 데이터를 공유합니다.
""")
