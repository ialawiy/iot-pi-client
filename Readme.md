Kode ini berjalan pada Raspberry Pi Zero W
Download dan jalankan `./install.sh` di terminal untuk menginstall node.js versi 16 dan menjalankan program

pipe.json adalah data-data dari firestore yang tersinkronasi secara otomatis ketika menjalankan `node ./js-client.js`, ubah data pada `['readings']` dan simpan file untuk melakukan sync dengan firestore database, data pada `['settings']` juga akan berubah secara realtime setiap ada perubahan pada database