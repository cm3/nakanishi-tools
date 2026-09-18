# 中西資料 IIIF Manifest 試験

NIHU の IIIF Image API を使いながら、別ホストの Presentation API 2 Manifest で「同じ面の別撮影画像」を表す試験です。画像ファイルはこのリポジトリに置きません。

## 内容

- `manifests/NAKANISHI_0209/manifest.json`: 表面と裏面を各1 Canvas とし、VL・IR・UVF・PLwDL・PLwoDL を `oa:Choice` にした Manifest。
- `manifests/NAKANISHI_0209/images.json`: Canvas ID、撮影対象、撮影方式、Image API サービスIDの対応表。Manifest の `seeAlso` から参照。
- `registration/0209-manifest-test.tsv`: 新しい試験レコードIDで `field_manifest` を指定する最小限の登録用 TSV。元の `NAKANISHI_0209` は上書きしない。
- `scripts/build_pilot.py`: 元の登録CSVと画像API `info.json` から上記JSONを再生成。
- `scripts/rebuild.sh`: 親プロジェクトの作業用CSVを参照して再生成する補助スクリプト。

## 公開と試験

1. GitHub Pages を `main` ブランチの `/ (root)` から公開する。想定URLは `https://cm3.github.io/nakanishi-tools/`。公開設定前は `field_manifest` のURLはアクセスできない。
2. Manifest と `images.json` のURLが HTTPS で取得でき、Manifest JSON の `@id` が公開URLと一致することを確認する。
3. `registration/0209-manifest-test.tsv` を試験登録し、NIHUの資料ページの Universal Viewer が外部 Manifest を読み込むか確認する。
4. 表面・裏面の切替と、各面の5方式の切替を確認する。`field_filepath` は試験TSVでは指定していない。

登録仕様は `field_manifest` を「外部サイトのマニフェストを利用してviewerを表示させる場合」の項目としている。ただし、NIHU の登録処理での実際の動作、設置済み Universal Viewer の Choice 対応は未確認。うまく表示されなければ、外部 Manifest URL が iframe に渡されているかを先に確認する。

## データ上の前提

生成器は元CSVの `field_filepath` の3階層目をファイル名、2階層目を `Front` / `Back` と読み、末尾の方式コードを `VL`、`IR`、`UVF`、`PLwDL`、`PLwoDL` として扱う。ここではこの10画像が同一面の別撮影であるという試験上の仮定を置いている。正確な撮影条件と位置合わせは撮影記録で確認する。

Manifest の Canvas は縮小画像に合わせて幅・高さを設定している。撮影画像の比率が異なる場合、ビューア上の重なりや切替位置は別途確認する。
