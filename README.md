# 中西資料 IIIF Manifest 試験

NIHU の IIIF Image API を使いながら、別ホストの Presentation API 2 / 3 Manifest で「同じ面の別撮影画像」を表す試験です。画像ファイルはこのリポジトリに置きません。[構造化パターンの比較](docs/patterns.md)に開発者向けの取得経路を記載しています。

同じ面の複数撮影画像で領域アノテーションを使う用途には、**v3 Choiceを第一候補**とします。表面・裏面を各1 Canvasにして、各面の5撮影画像をそのCanvas内に置く構造です。ビューアのページ表示は2枚でも、Manifestには計10画像が入っています。利用側で撮影方式を切り替えられるかは別途確認が必要です。v2 Rangeとv3 Rangeは各画像が別Canvasになるため、注釈を別撮影画像にも表示するには利用側の対応付けが必要です。前提と制約は[推奨理由](docs/patterns.md#推奨-アノテーション利用には-v3-choice)を参照してください。

## 内容

- `manifests/NAKANISHI_0209/manifest.json`: 表面と裏面のVL・IR・UVF・PLwDL・PLwoDL を各1 Canvas にした Manifest。`sc:Range` で表面と裏面の各5 Canvas をグループ化する。NIHUに設置されたUniversal Viewerで画像URLを取得できる形。
- `manifests/NAKANISHI_0209/images.json`: Canvas ID、撮影対象、撮影方式、Image API サービスIDの対応表。Manifest の `seeAlso` から参照。
- `manifests/NAKANISHI_0209/manifest-v3-ranges.json`: v3 の10 Canvas + 表裏Range。
- `manifests/NAKANISHI_0209/manifest-v3-choice.json`: v3 の表裏2 Canvas + 撮影方式Choice。
- `manifests/NAKANISHI_0209/images-v3-*.json`: v3各パターンの対応表。
- `registration/0209-manifest-test.tsv`: 新しい試験レコードIDで `field_manifest` を指定する最小限の登録用 TSV。元の `NAKANISHI_0209` は上書きしない。
- `registration/0209-v3-ranges-test.tsv`、`0209-v3-choice-test.tsv`: v3の2パターンを別IDで試す最小限の登録用 TSV。親プロジェクトの `work/2026-09-18-external-manifest-pilot/` には元の34列を維持したCSVもある。
- 3件の `title` は公開一覧で区別できるよう、`【IIIF比較実験｜v2 Range】`、`【IIIF比較実験｜v3 Range】`、`【IIIF比較実験｜v3 Choice】` で始める。`field_title` の原資料名は共通。
- `scripts/build_pilot.py`: 元の登録CSVと画像API `info.json` から上記JSONを再生成。
- `scripts/rebuild.sh`: 親プロジェクトの作業用CSVを参照して再生成する補助スクリプト。

## 公開と試験

1. GitHub Pages の公開URL `https://cm3.github.io/nakanishi-tools/` から各Manifestを取得する。
2. Manifest と `images.json` のURLが HTTPS で取得でき、Manifest JSON の `@id` が公開URLと一致することを確認する。
3. `registration/0209-manifest-test.tsv` を試験登録し、NIHUの資料ページの Universal Viewer が外部 Manifest を読み込むか確認する。
4. v2では10 Canvas の表示と画像表示を確認する。v3ではRangeとChoiceを別々の試験レコードで確認する。`field_filepath` は試験TSVでは指定していない。

登録仕様は `field_manifest` を「外部サイトのマニフェストを利用してviewerを表示させる場合」の項目としている。初版のv2 `oa:Choice` 試作時にNIHU設置版Universal Viewerで「There is no dataUri to fetch」が出たため、v2公開例を各Canvasに画像を直接置くRange構成に変更した。ただし、当時のエラー原因をChoiceと特定できておらず、v2 Choiceの可否は未検証。同一面の別撮影という機械可読な関係は、現在のv2公開例では `structures` の `sc:Range` と、`seeAlso` の `images.json` にある `view_id` で取得する。

## データ上の前提

生成器は元CSVの `field_filepath` の3階層目をファイル名、2階層目を `Front` / `Back` と読み、末尾の方式コードを `VL`、`IR`、`UVF`、`PLwDL`、`PLwoDL` として扱う。ここではこの10画像が同一面の別撮影であるという試験上の仮定を置いている。正確な撮影条件と位置合わせは撮影記録で確認する。

Manifest の Canvas は縮小画像に合わせて幅・高さを設定している。Canvas 間の位置合わせは表現していない。
