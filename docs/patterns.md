# 同一資料・別撮影画像の構造化サンプル

同じ `NAKANISHI_0209` の10画像を使う。既存の3例は NIHU Image API 2.1、新しいChoice試験版は Image API 3.0 から画像を配信する。Manifest の配信と画像配信のサーバーは独立している。各Manifestの `id` / `@id` はそのJSONの公開URLに一致する。

| パターン | Manifest | 撮影対象のまとまり | 画像の選択 | NIHU設置版ビューアでの確認 |
| --- | --- | --- | --- | --- |
| v2 Canvas + Range | [manifest.json](../manifests/NAKANISHI_0209/manifest.json) | `structures` の表面・裏面の `sc:Range` | 各画像は独立したCanvas | 2026-09-18に表示を確認 |
| v3 Canvas + Range | [manifest-v3-ranges.json](../manifests/NAKANISHI_0209/manifest-v3-ranges.json) | `structures` の表面・裏面の `Range` | 各画像は独立したCanvas | 2026-09-18に画像表示を確認 |
| v3 Canvas + Choice | [manifest-v3-choice.json](../manifests/NAKANISHI_0209/manifest-v3-choice.json) | 表面・裏面それぞれ1 Canvas | Canvas内の `Choice.items` に各5画像 | 公式UV4では撮影方式を切替可能。NIHU設置版では表裏2ページは表示するが、撮影方式は切替不可。注釈の挙動は未確認 |
| v3 Choice + Image API 3.0 | [manifest-v3-choice-image3.json](../manifests/NAKANISHI_0209/manifest-v3-choice-image3.json) | 表面・裏面それぞれ1 Canvas | 上のChoiceと同じ10画像。画像サービスは `ImageService3` | 公開後のビューア表示は未確認 |

Image API 3.0 版は、Presentation API 3.0 のChoiceを変えず、画像・サムネイルのURLを `/iiif/3/` に、サービス記述を `type: ImageService3` と `profile: level2` にしたもの。対応表は [images-v3-choice-image3.json](../manifests/NAKANISHI_0209/images-v3-choice-image3.json)。NIHUの公開Image API 3.0で `info.json` と画像を取得できることを確認して生成している。GitHub Pagesへのpush後、[公式UV4で開く](https://uv-v4.netlify.app/#?manifest=https://cm3.github.io/nakanishi-tools/manifests/NAKANISHI_0209/manifest-v3-choice-image3.json)ことができる。NIHUの資料ページで試すには別の登録レコードの `field_manifest` にこのURLを設定する。既存の比較レコードは変更していない。

公開一覧では3件を並べて比較する想定。登録レコードの `title` は `【IIIF比較実験｜v2 Range】文学書　紙片`、`【IIIF比較実験｜v3 Range】文学書　紙片`、`【IIIF比較実験｜v3 Choice】文学書　紙片` とし、原資料名を表す `field_title` は共通に保つ。登録IDと `field_weight` は各パターンで別にする。

## 推奨: アノテーション利用には v3 Choice

今回の主目的は「同じ資料の同じ面を異なる方法で撮影した画像を切り替え、面上の注釈を使う」こと。v3 Choiceでは、表面と裏面を各1 Canvasにし、そのCanvasのpainting Annotationの `body` に5撮影方式の `Choice` を置く。**2 Canvasは2画像だけという意味ではなく、2面に計10画像が含まれる。** 利用側がChoiceを解釈して画像を切り替えられれば、Canvas IDを面の識別子として扱い、そのCanvas上の領域に付けた注釈を撮影方式の切替後にも表示できる。IIIFの[複数画像のChoiceの用例](https://iiif.io/api/cookbook/recipe/0033-choice/)も、位置を合わせた撮影画像とCanvas対象の注釈を想定している。

| 観点 | v3 Choice（推奨） | v2 Range / v3 Range（比較用） |
| --- | --- | --- |
| 10画像の表現 | 表裏2 Canvas、各Canvasに5画像のChoice | 10画像がそれぞれ独立したCanvas |
| 同じ面の別撮影画像という関係 | 1 Canvasの選択肢として直接表現 | 表裏Rangeに属するCanvasとして表現。各Canvasの撮影方式の識別にはラベルや `seeAlso` の対応表を参照 |
| 領域注釈の対象 | 表面または裏面のCanvasを対象にできる | 特定の撮影画像のCanvasを対象にする。別撮影画像へ表示するには利用側が同じ面のCanvasを対応付け、注釈を複製または座標変換する必要がある |
| ページ送り | 表面・裏面の2 Canvas | 撮影方式もページとして並ぶ10 Canvas |

Rangeは閲覧順序や章・面などのまとまりを表す標準構造であり、Rangeに入れた複数Canvasを同一座標の画像として扱う指示ではない。このため、この用途ではRangeだけを根拠に領域注釈を共有できない。`seeAlso` の `images*.json` は撮影方式を固定コードで取得する補助データだが、独立Canvas間の注釈共有を自動化する標準機能ではない。

この比較で推奨度が低いのは、**現在公開しているv2 Range案とv3 Range案**である。v2の仕様全体がこの用途に不向きという意味ではない。初期にはv2 `oa:Choice` で表裏2 Canvas・計10画像とした試作もあったが、当時の表示エラーはキャッシュなど他の要因と切り分けられていない。その試作は現在公開しておらず、v2 Choiceの互換性について結論は出していない。

NIHU設置版ビューアでv3 Choiceの**表裏2ページが表示されること**と、各ページの**5撮影方式を選択できること**は別の確認事項。2026-09-18の利用者確認では、公式UV4でこのManifestの撮影方式を切り替えられた一方、NIHU設置版では切り替えられなかった。Manifestには計10画像が含まれ、UV4で動作するため、少なくとも「Manifestに2画像しかない」という問題ではない。NIHU画面で10画像をすべてページ送りで見せたい場合は、Range案が適する。

NIHUの資料ページは `/libraries/uv/uv.html` をiframeで読み込む。IIIFの[ビューア対応表](https://iiif.io/api/cookbook/recipe/matrix/)でもUniversal Viewerは[複数画像のChoice](https://iiif.io/api/cookbook/recipe/0033-choice/)に対応とされ、[公式UV4でこのManifestを開く](https://uv-v4.netlify.app/#?manifest=https://cm3.github.io/nakanishi-tools/manifests/NAKANISHI_0209/manifest-v3-choice.json)試験でも切替を確認した。NIHU設置版の公開 `uv.html` と `uv.js` には製品版番号の明示が見つからず、正確な版は未特定（`uv.js` 内の依存ライブラリの版番号はUV本体の版番号ではない）。NIHU側で更新を検討する場合は、設置版の管理情報で版を確認し、UV4を検証環境に導入してiframe連携・表示設定・既存資料への影響を確認する。注釈エディタでのChoice対応は別途検証する。

なお「同一アイテム」は表裏を含む資料全体の関係で、矩形領域の注釈を表面から裏面へ同じ座標で表示してよいという意味ではない。v3 Choiceでも、同じ面の別撮影画像が位置合わせされていなければ領域注釈はずれる。正確な撮影条件と画像間の位置合わせ、IIIF Semantic EditorによるChoiceの読み込み・切替・Canvas対象注釈の表示は別途検証する。注釈をManifestで表現・配信する場合は[Presentation API 3.0のCanvas annotations](https://iiif.io/api/presentation/3.0/#annotations)を参照する。

v3の2ファイルは [IIIF Presentation Validatorのv3 JSON Schema](https://github.com/IIIF/presentation-validator/blob/main/schema/iiif_3_0.json) で検証した。Manifestから取り出した撮影対象2群・画像10件と、それぞれの `seeAlso` 対応表も一致する。Choiceの切替操作は公式UV4とNIHU設置版で比較した。注釈の挙動は別途確認する。

NIHU設置版ビューアはv3 Canvasからサムネイルの画像サービスを推定できず、画像IDが欠けた `/full/200,/0/default.jpg` を要求した。v3サンプルではManifest、Canvas、Choice内の各画像に `thumbnail` を明示し、NIHU Image APIの絶対URLを指定する。

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
- [Image API 3.0](https://iiif.io/api/image/3.0/)
