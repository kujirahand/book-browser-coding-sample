// ブロックしたいパターンを指定 --- (*1)
const block_list = [
    '.ad',
    '.ads',
    '.banner',
    '.subAdBannerArea',
    '.adsbygoogle',
    '.pickCreative_root',
    '.myPickModule_link',
]
const pattern = block_list.join(',')
// パターンにマッチする要素を列挙して削除 --- (*2)
document.querySelectorAll(pattern).forEach((element) => {
    element.remove();
});
