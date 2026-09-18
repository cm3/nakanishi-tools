# 中西資料 IIIF Manifest 試験

NIHU の IIIF Image API を使いながら、別ホストの Presentation API 2 Manifest で「同じ面の別撮影画像」を表す試験です。画像ファイルはこのリポジトリに置きません。

## 内容

- `manifests/NAKANISHI_0209/manifest.json`: 表面と裏面のVL・IR・UVF・PLwDL・PLwoDL を各1 Canvas にした Manifest。`sc:Range` で表面と裏面の各5 Canvas をグループ化する。NIHUに設置されたUniversal Viewerで画像URLを取得できる形。
- `manifests/NAKANISHI_0209/images.json`: Canvas ID、撮影対象、撮影方式、Image API サービスIDの対応表。Manifest の `seeAlso` から参照。
- `registration/0209-manifest-test.tsv`: 新しい試験レコードIDで `field_manifest` を指定する最小限の登録用 TSV。元の `NAKANISHI_0209` は上書きしない。
- `scripts/build_pilot.py`: 元の登録CSVと画像API `info.json` から上記JSONを再生成。
- `scripts/rebuild.sh`: 親プロジェクトの作業用CSVを参照して再生成する補助スクリプト。

## 公開と試験

1. GitHub Pages を `main` ブランチの `/ (root)` から公開する。想定URLは `https://cm3.github.io/nakanishi-tools/`。公開設定前は `field_manifest` のURLはアクセスできない。
2. Manifest と `images.json` のURLが HTTPS で取得でき、Manifest JSON の `@id` が公開URLと一致することを確認する。
3. `registration/0209-manifest-test.tsv` を試験登録し、NIHUの資料ページの Universal Viewer が外部 Manifest を読み込むか確認する。
4. 10 Canvas の表示と、各 Canvas の画像表示を確認する。`field_filepath` は試験TSVでは指定していない。

登録仕様は `field_manifest` を「外部サイトのマニフェストを利用してviewerを表示させる場合」の項目としている。初版の `oa:Choice` はNIHUに設置されたUniversal Viewerで「There is no dataUri to fetch」を起こしたため、画像を各Canvasの直接 `resource` に変更した。同一面の別撮影という機械可読な関係は `structures` の `sc:Range` と、`seeAlso` の `images.json` にある `view_id` で取得する。

## データ上の前提

生成器は元CSVの `field_filepath` の3階層目をファイル名、2階層目を `Front` / `Back` と読み、末尾の方式コードを `VL`、`IR`、`UVF`、`PLwDL`、`PLwoDL` として扱う。ここではこの10画像が同一面の別撮影であるという試験上の仮定を置いている。正確な撮影条件と位置合わせは撮影記録で確認する。

Manifest の Canvas は縮小画像に合わせて幅・高さを設定している。Canvas 間の位置合わせは表現していない。
