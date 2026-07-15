# Hatch

[English](README.md) | [한국어](README.ko.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [Français](README.fr.md) | [Español](README.es.md)

## 마음껏 만들고, 깔끔하게 공개하세요.

Hatch는 혼자 만드는 이에게 탐색을 위한 비공개 workbench와 공유를 위한
정돈된 product 공간을 제공합니다. 둘 사이의 경계를 분명히 하므로, 공개할
때마다 같은 요구 사항을 다시 정리할 필요가 없습니다.

## 빠른 시작

Hatch를 설치한 뒤 `$hatch`로 프로젝트를 시작하세요. workbench, product,
평가 증거를 위한 독립적인 로컬 Git 저장소를 만듭니다.

제품 버전이 준비되면 다시 `$hatch`를 사용해 승격하세요. Hatch는 범위를
확인하고, 버전과 변경 로그를 기록하며, 정확한 커밋을 감사한 뒤 푸시할
준비가 되었는지 판단합니다.

## 워크스페이스 구조

`$hatch init`은 아래와 같은 로컬 컨테이너를 만듭니다. 세 하위 디렉터리는
서로 독립된 Git 저장소입니다.

```text
my-project/
├── hatch.toml                  # 세 경계를 설명하는 설정
├── my-project-workbench/       # 비공개 초안, 실험, brief
├── my-project-product/         # 공개해도 안전한 product 소스
└── my-project-evals/           # 비공개 사람 또는 자동 평가 증거
```

## 명령

Hatch의 사용자용 명령은 두 개입니다. 뒤의 단계들은 외울 명령이 아니라
`promote` 안에서 신중하게 진행되는 과정입니다.

### `init`

새 프로젝트를 시작할 때 `$hatch init`을 사용하세요.

1. 상위 디렉터리, 프로젝트 이름, 공개 Git ID를 정합니다.
2. `--dry-run`이면 컨테이너와 세 저장소의 경로만 출력합니다.
3. 그 외에는 컨테이너를 만들고 `workbench`, `product`, `evals`를 각각
   `main` 브랜치의 독립된 Git 저장소로 초기화합니다.
4. `hatch.toml`, 비공개 workbench 감사 정책, 저장소 안내, ignore 파일,
   product의 초기 `VERSION`(`0.0.0`)과 `CHANGELOG.md`를 작성합니다.
5. product 저장소에 공개 Git ID를 설정합니다.

원격 저장소 생성, 커밋, 푸시, 태그, 릴리스, 배포는 절대 하지 않습니다.

### `promote`

선택한 작업을 product 스냅샷으로 만들 준비가 되었을 때 `$hatch promote`를
사용하세요.

1. product를 바꾸지 않고 후보, 현재 product 상태, 기존 evidence를 살펴봅니다.
2. 의도, 포함·제외 범위, 공개 안전성 판단, 승인 기준, evidence, 다음 안정 버전을
   기록하는 source-pinned Promotion Brief를 만듭니다.
3. brief를 보여주고 product 변경 전 사용자 확인을 받습니다.
4. 확인된 범위만 product에 반영합니다. workbench 전체를 자동 동기화하지 않습니다.
5. `VERSION`과 일치하는 `CHANGELOG.md` 항목을 작성하고, 관련 product 검증을
   실행한 뒤 하나의 정확한 product 커밋을 만듭니다.
6. private 정책에 따라 그 정확한 커밋의 도달 가능한 이력, 커밋 메시지, Git ID,
   경로, 파일 내용을 감사합니다.
7. 같은 커밋에 대한 사람·자동·혼합 평가 evidence를 기록합니다.
8. ready check를 실행합니다. brief, 버전 로그, 감사, evidence가 모두 같은 커밋을
   가리키는지 확인하고 `READY TO PUSH`, `NOT READY`, `NEEDS EVIDENCE` 중 하나를
   보고합니다.

`promote`가 직접 푸시, 태그, 릴리스 생성, 배포를 하지는 않습니다.

## Hatch가 필요한 이유

### workbench와 product는 다릅니다

**문제.** 프로젝트에는 초안, 실험, 메모, 미완성 작업을 담을 공간이
필요합니다. 공개 저장소에는 집중된 안전한 스냅샷이 필요합니다. 둘을 섞으면
매 릴리스가 정리 작업이 됩니다.

**해결.** 두 공간을 독립적인 Git 저장소로 유지합니다. workbench에서는
자유롭게 개발하고, product에는 공개할 작업만 승격합니다.

### 승격은 반복 가능해야 합니다

**문제.** 승격할 때마다 같은 질문이 돌아옵니다. 무엇이 포함되는가? 공개해도
안전한가? 이번 버전은 무엇인가? 실제로 테스트했는가?

**해결.** Hatch는 brief, 버전, 감사, 평가 증거, 준비 상태 결정을 하나의
흐름으로 만듭니다. 모두 하나의 정확한 product 커밋에 연결됩니다.

### 요약

Hatch는 비공개 탐색과 공개 product 작업을 분리하고, 둘 사이의 이동을 작고
신중하며 검증 가능하게 만듭니다.
