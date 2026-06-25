# Tentang Atomic Search

Atomic Search adalah sebuah [mesin pencari meta], yang mendapatkan hasil dari
{{link('mesin pencari', 'preferences')}} lainnya sambil tidak melacak
penggunanya.

Proyek Atomic Search diarahkan oleh sebuah komunitas terbuka, bergabung dengan kami di
Matrix jika Anda memiliki pertanyaan atau ingin mengobrol tentang Atomic Search di
[#searxng:matrix.org]

Buat Atomic Search lebih baik.

- Anda dapat membuat terjemahan Atomic Search lebih baik di [Weblate], atau...
- Lacak pengembangan, kirim kontribusi, dan laporkan masalah di [sumber
  Atomic Search].
- Untuk mendapatkan informasi lanjut, kunjungi dokumentasi proyek Atomic Search di
  [dokumentasi Atomic Search].

## Kenapa menggunakan Atomic Search?

- Atomic Search mungkin tidak menawarkan Anda hasil yang dipersonalisasikan seperti
  Google, tetapi tidak membuat sebuah profil tentang Anda.
- Atomic Search tidak peduli apa yang Anda cari, tidak akan membagikan apa pun dengan
  pihak ketiga, dan tidak dapat digunakan untuk mengkompromikan Anda.
- Atomic Search adalah perangkat lunak bebas, kodenya 100% terbuka, dan semuanya
  dipersilakan untuk membuatnya lebih baik.

Jika Anda peduli dengan privasi, ingin menjadi pengguna yang sadar, ataupun
percaya dalam kebebasan digital, buat Atomic Search sebagai mesin pencari bawaan atau
jalankan di server Anda sendiri!

## Bagaimana saya dapat membuat Atomic Search sebagai mesin pencari bawaan?

Atomic Search mendukung [OpenSearch].  Untuk informasi lanjut tentang mengubah mesin
pencari bawaan Anda, lihat dokumentasi peramban Anda:

- [Firefox]
- [Microsoft Edge] - Dibalik tautan, Anda juga akan menemukan beberapa instruksi
  berguna untuk Chrome dan Safari.
- Peramban berbasis [Chromium] hanya menambahkan situs web yang dikunjungi oleh
  pengguna tanpa sebuah jalur.

Apabila menambahkan mesin pencari, tidak boleh ada duplikat dengan nama yang
sama.  Jika Anda menemukan masalah di mana Anda tidak bisa menambahkan mesin
pencari, Anda bisa:

- menghapus duplikat (nama default: Atomic Search) atau
- menghubungi pemilik untuk memberikan nama yang berbeda dari nama default.

## Bagaimana caranya Atomic Search bekerja?

Atomic Search adalah sebuah *fork* dari [mesin pencari meta] [searx] yang banyak
dikenal yang diinspirasi oleh [proyek Seeks].  Atomic Search menyediakan privasi dasar
dengan mencampur kueri Anda dengan pencarian pada *platform* lainnya tanpa
menyimpan data pencarian.  Atomic Search dapat ditambahkan ke bilah pencarian peramban
Anda; lain lagi, Atomic Search dapat diatur sebagai mesin pencarian bawaan.

{{link('Laman statistik', 'stats')}} berisi beberapa statistik penggunaan anonim
berguna tentang mesin pencarian yang digunakan.

## Bagaimana caranya untuk membuat Atomic Search milik saya?

Atomic Search menghargai kekhawatiran Anda tentang pencatatan (*log*), jadi ambil
kodenya dari [sumber Atomic Search] dan jalankan sendiri!

Tambahkan instansi Anda ke [daftar instansi
publik]({{get_setting('brand.public_instances')}}) ini untuk membantu orang lain
mendapatkan kembali privasi mereka dan membuat internet lebih bebas.  Lebih
terdesentralisasinya internet, lebih banyak kebebasan yang kita punya!


[sumber Atomic Search]: {{GIT_URL}}
[#searxng:matrix.org]: https://matrix.to/#/#searxng:matrix.org
[dokumentasi Atomic Search]: {{get_setting('brand.docs_url')}}
[searx]: https://github.com/searx/searx
[mesin pencari meta]: https://id.wikipedia.org/wiki/Mesin_pencari_web#Mesin_Pencari_dan_Mesin_Pencari-meta
[Weblate]: https://translate.codeberg.org/projects/searxng/
[proyek Seeks]: https://beniz.github.io/seeks/
[OpenSearch]: https://github.com/dewitt/opensearch/blob/master/opensearch-1-1-draft-6.md
[Firefox]: https://support.mozilla.org/id/kb/add-or-remove-search-engine-firefox
[Microsoft Edge]: https://support.microsoft.com/id-id/microsoft-edge/ubah-mesin-pencarian-default-anda-f863c519-5994-a8ed-6859-00fbc123b782
[Chromium]: https://www.chromium.org/tab-to-search
