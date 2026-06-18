# 대봉 업무 시스템 분리 버전

기존 `app(14).py`를 업무별로 나눈 구조입니다.

## 파일 구조

```
daebong_split_system/
├─ app.py              # 안내용 첫 화면
├─ erp_app.py          # 거래처/출고일지/기사/경비 관리
├─ quote_app.py        # 견적 작성/저장된 견적서/PDF 출력
├─ requirements.txt
└─ database/           # 실행하면 자동 생성, JSON 데이터 공유
```

## 실행 방법

ERP 앱:
```bash
streamlit run erp_app.py --server.port 8501
```

견적서 앱:
```bash
streamlit run quote_app.py --server.port 8502
```

## 서버 배포 추천

- AWS Lightsail 2GB RAM 이상 권장
- 직원 동시 사용이 많아지면 4GB RAM 권장
- `database/` 폴더는 반드시 백업하세요.

## 핵심 변경점

- 견적서 기능과 출고/거래처 관리 기능을 분리
- 두 앱이 같은 `database/` 폴더를 사용하도록 변경
- 기존 JSON 저장 방식 유지
- 기존 화면과 계산 로직 최대한 보존
