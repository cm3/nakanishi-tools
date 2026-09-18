# 同一資料・別撮影画像の構造化サンプル

同じ `NAKANISHI_0209` の10画像を使い、画像はすべて NIHU Image API v2 から配信する。Manifest の配信と画像配信のサーバーは独立している。各Manifestの `id` / `@id` はそのJSONの公開URLに一致する。

| パターン | Manifest | 撮影対象のまとまり | 画像の選択 | NIHU設置版ビューアでの確認 |
| --- | --- | --- | --- | --- |
| v2 Canvas + Range | [manifest.json](../manifests/NAKANISHI_0209/manifest.json) | `structures` の表面・裏面の `sc:Range` | 各画像は独立したCanvas | 2026-09-18に表示を確認 |
| v3 Canvas + Range | [manifest-v3-ranges.json](../manifests/NAKANISHI_0209/manifest-v3-ranges.json) | `structures` の表面・裏面の `Range` | 各画像は独立したCanvas | 未確認 |
| v3 Canvas + Choice | [manifest-v3-choice.json](../manifests/NAKANISHI_0209/manifest-v3-choice.json) | 表面・裏面それぞれ1 Canvas | Canvas内の `Choice.items` から1画像を選択 | 未確認 |

公開一覧では3件を並べて比較する想定。登録レコードの `title` は `【IIIF比較実験｜v2 Range】文学書　紙片`、`【IIIF比較実験｜v3 Range】文学書　紙片`、`【IIIF比較実験｜v3 Choice】文学書　紙片` とし、原資料名を表す `field_title` は共通に保つ。登録IDと `field_weight` は各パターンで別にする。

`Choice` は同じ対象に対する相互に選択可能な画像を示す。`Range` はCanvasのグループを示し、それだけでは「画像を切り替える」動作は指示しない。v3 Choiceは撮影方式の違いをIIIFの標準構造で最も直接的に表す。一方、NIHUの設置版Universal Viewerではv2 Choiceを表示できなかったため、v3 Choiceの表示も試験する必要がある。

v3の2ファイルは [IIIF Presentation Validatorのv3 JSON Schema](https://github.com/IIIF/presentation-validator/blob/main/schema/iiif_3_0.json) で検証した。Manifestから取り出した撮影対象2群・画像10件と、それぞれの `seeAlso` 対応表も一致する。ビューアの表示と切替操作は別途確認する。

各Manifestの `seeAlso` に、対応する `images*.json` を指定した。そこでは `view_id`（`front` / `back`）、`modality_code`（`VL` 等）、`image_service_id` を明示している。IIIFの `label` や `metadata` は表示用なので、安定したコードとして扱う場合はこの対応表を使う。`scripts/inspect_patterns.py` は各Manifestから標準のRangeまたはChoiceをたどり、撮影対象ごとの画像サービスIDを取り出す利用例。

## 利用開発者向けの確認点

1. Manifest JSONを取得し、v2なら `@context`、v3なら `@context` と `type` を確認する。
2. v2 / v3 Range型では `structures` の表面・裏面Rangeをたどり、各Canvasのpainting画像を取得する。
3. v3 Choice型ではCanvasのpainting Annotationの `body.items` をたどり、各画像の `service` を取得する。
4. 撮影方式の固定コードや初期表示画像は `seeAlso` の対応表で照合する。

ここではファイル名の `Front` / `Back` と方式の末尾コードを元CSVから解釈している。正確な撮影条件や画像同士の位置合わせは撮影記録で確認する。Choice型のCanvas寸法は各画像の縮小版の最大値を使うため、画像の縦横比に差がある場合の切替表示も確認対象である。

## 仕様例

- [Presentation API 3.0](https://iiif.io/api/presentation/3.0/)
- [IIIF Cookbook: 複数画像のChoice](https://iiif.io/api/cookbook/recipe/0033-choice/)
- [IIIF Cookbook: Image APIを使うManifest](https://iiif.io/api/cookbook/recipe/0005-image-service/)
