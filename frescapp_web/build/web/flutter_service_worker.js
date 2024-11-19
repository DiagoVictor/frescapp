'use strict';
const MANIFEST = 'flutter-app-manifest';
const TEMP = 'flutter-temp-cache';
const CACHE_NAME = 'flutter-app-cache';

const RESOURCES = {"assets/AssetManifest.bin": "2190759334add09e527bceb39fd189e6",
"assets/AssetManifest.bin.json": "9c5eaf8d1cfd709d32e68189fc5b9820",
"assets/AssetManifest.json": "5864beb8f19238a0e1515c8d22830a2c",
"assets/FontManifest.json": "866b9b20ab0e8c30ffe220d2a2d66abe",
"assets/fonts/MaterialIcons-Regular.otf": "d9b24771b54204e5e802e49bcf893a85",
"assets/images/icon_app.png": "68d70a7f689185f1156029565dd193eb",
"assets/images/start_icon.png": "13deee1e58242605aab4116f8644c99b",
"assets/NOTICES": "d37481f3abfef2652df606728965b6be",
"assets/packages/cupertino_icons/assets/CupertinoIcons.ttf": "e986ebe42ef785b27164c36a9abc7818",
"assets/packages/syncfusion_flutter_pdfviewer/assets/fonts/RobotoMono-Regular.ttf": "5b04fdfec4c8c36e8ca574e40b7148bb",
"assets/packages/syncfusion_flutter_pdfviewer/assets/highlight.png": "7384946432b51b56b0990dca1a735169",
"assets/packages/syncfusion_flutter_pdfviewer/assets/squiggly.png": "c9602bfd4aa99590ca66ce212099885f",
"assets/packages/syncfusion_flutter_pdfviewer/assets/strikethrough.png": "cb39da11cd936bd01d1c5a911e429799",
"assets/packages/syncfusion_flutter_pdfviewer/assets/underline.png": "c94a4441e753e4744e2857f0c4359bf0",
"assets/products/BOG-CAT001-00001.png": "12363d2c8f27c79c2e8c67e3c1620ed9",
"assets/products/BOG-CAT001-00002.png": "e3cc9efb014cfaaae56b284dcf2d023a",
"assets/products/BOG-CAT001-00003.png": "4c065a9d6d80d00ec5fa0a6608df7065",
"assets/products/BOG-CAT001-00004.png": "81507480e0936da2e6e536a576a5307e",
"assets/products/BOG-CAT001-00005.png": "f9832154817fa0e1466dbddf77c4d6e7",
"assets/products/BOG-CAT001-00006.png": "4910cfe482fd0c879fc50c0ae6546d7f",
"assets/products/BOG-CAT001-00007.png": "8f7a99f9d5d31b8bbc5696f361d7e1f1",
"assets/products/BOG-CAT001-00008.png": "6ad0fe2a251a366cb95754998ebd8b68",
"assets/products/BOG-CAT001-00009.png": "daa5f597f60d1adc146f5931d740ac24",
"assets/products/BOG-CAT001-00010.png": "80ae715c02f0c6b65e792e38e2048076",
"assets/products/BOG-CAT001-00011.png": "60efb2f1f3bf6669a310e8b89662b68f",
"assets/products/BOG-CAT001-00012.png": "9d7f79cb0ca0ae390fd36704835250b6",
"assets/products/BOG-CAT001-00013.png": "38ec2b50298bfd6d4b1d94eb54f5604b",
"assets/products/BOG-CAT001-00014.png": "1b1cc2d4db91b3afec943a8a1ddd3e74",
"assets/products/BOG-CAT001-00015.png": "1b0a6f01ecb61d70eaafc887c2f58b42",
"assets/products/BOG-CAT001-00016.png": "4a49b603fef397749a5ef0e9addca0a9",
"assets/products/BOG-CAT001-00017.png": "db2a64f84e2d5a57f6fb138836502220",
"assets/products/BOG-CAT001-00018.png": "2790f54bd292aeb27b434c4eb40a9ff0",
"assets/products/BOG-CAT001-00019.png": "d41d8cd98f00b204e9800998ecf8427e",
"assets/products/BOG-CAT001-00020.png": "bdd008536fb0251f3f00dcf9b83488de",
"assets/products/BOG-CAT001-00021.png": "0a496a3a013c06089c282dcde61d9d1d",
"assets/products/BOG-CAT001-00022.png": "b667ee0fec4c3e2fe9afd0e73064877b",
"assets/products/BOG-CAT001-00023.png": "9e99e50bc25b8322f1d0268875c7208f",
"assets/products/BOG-CAT001-00024.png": "7db66d6fd30b18d7aa4d8a913ae6a416",
"assets/products/BOG-CAT001-00025.png": "1047cfbc476d8484925773e99da1a2ef",
"assets/products/BOG-CAT001-00026.png": "df54610dcfb6216a03bf5f7dbab544dc",
"assets/products/BOG-CAT001-00027.png": "5342eb370aaef6e1c94d6d4abe4c4e0c",
"assets/products/BOG-CAT002-00001.png": "7634efd3989ebb4cf051d9252e4566ee",
"assets/products/BOG-CAT002-00002.png": "26364df9527b970298f3692d2f4bd084",
"assets/products/BOG-CAT002-00003.png": "c9f7227e4de907b84846bea325131161",
"assets/products/BOG-CAT002-00004.png": "4dc97f17c34c3f0f45b7ea7b61cc56c5",
"assets/products/BOG-CAT002-00005.png": "cc35e8b20d9b2d8ae65a3b277304b280",
"assets/products/BOG-CAT002-00006.png": "8fec2a94405c6961408707504daccb7b",
"assets/products/BOG-CAT002-00007.png": "353d1a13705cb9562668b11aeb2cf14f",
"assets/products/BOG-CAT002-00008.png": "fab7b394be351ec179791297f0ed5a70",
"assets/products/BOG-CAT002-00009.png": "9d77530d6856ce5f05b7bb7975d7b9fe",
"assets/products/BOG-CAT002-00010.png": "ab03dba1a57562c0ed404ade40c425d4",
"assets/products/BOG-CAT002-00011.png": "ce0b285054558bb4b975e8c3ae3308bc",
"assets/products/BOG-CAT002-00012.png": "186670b0fc9618e50de8724112207c03",
"assets/products/BOG-CAT002-00013.png": "97ed9f6232afbff6166bc63ce5a2c967",
"assets/products/BOG-CAT002-00014.png": "a7d588f1e86f79a38cc798375d6661f7",
"assets/products/BOG-CAT002-00015.png": "bf6f08963be381b20d69e4b4e0c6ef67",
"assets/products/BOG-CAT002-00016.png": "8be51cea7b001cce3d6cc2cee3f0d4c0",
"assets/products/BOG-CAT002-00017.png": "9950db2ffdaf90c542e72c9623e7d3a4",
"assets/products/BOG-CAT003-00001.png": "b68ccffb08a55084314bb770d742ad55",
"assets/products/BOG-CAT003-00002.png": "38466d47a0360a677bdf7e160c9bdb4a",
"assets/products/BOG-CAT003-00003.png": "06e2ad6acf700d48eb044f2f71c49e12",
"assets/products/BOG-CAT003-00004.png": "768baccb7ce98011bd5a4d77bdde7df8",
"assets/products/BOG-CAT003-00005.png": "353fbc6694645294f2fed49c9637f23d",
"assets/products/BOG-CAT003-00006.png": "5305032fd5948554bb0fab9c039c04d6",
"assets/products/BOG-CAT004-00001.png": "4946591b559e09de654199f6b93a0b08",
"assets/products/BOG-CAT004-00002.png": "b93aded4c4a435ebf7626d5972fb26db",
"assets/products/BOG-CAT004-00003.png": "517a392f3d347873833ae7eec67593e3",
"assets/products/BOG-CAT004-00004.png": "49dc009032f63ccd69da2e314d9b957b",
"assets/products/BOG-CAT004-00005.png": "f40f36d4e9fe1c9d4b182801a28904d2",
"assets/products/BOG-CAT004-00006.png": "73fe7414e83337643effc762207fbb62",
"assets/products/BOG-CAT004-00007.png": "5ae735679988a98103f62b336f6339f9",
"assets/products/BOG-CAT004-00008.png": "830cc5c64beb42221bf88bf5312cb99a",
"assets/products/BOG-CAT004-00009.png": "a6610fc8b83e58ed7869cae7eb7cb215",
"assets/products/BOG-CAT004-00010.png": "92d6e5459dad7de8570438f982fa1908",
"assets/products/BOG-CAT004-00011.png": "d41d8cd98f00b204e9800998ecf8427e",
"assets/products/BOG-CAT004-00012.png": "b1d29bb933d0c88d0a993db89145adc6",
"assets/products/BOG-CAT004-00013.png": "be7b1525a691b3cf9e4988851636ab3a",
"assets/products/BOG-CAT004-00014.png": "2f4eebcac10b269750816f3fdc047bb7",
"assets/products/diago.png": "385c3dbc93d576269c40b675eb6a7547",
"assets/shaders/ink_sparkle.frag": "ecc85a2e95f5e9f53123dcaf8cb9b6ce",
"assets/web/assets/images/icon_app.png": "68d70a7f689185f1156029565dd193eb",
"assets/web/assets/images/start_icon.png": "13deee1e58242605aab4116f8644c99b",
"canvaskit/canvaskit.js": "5fda3f1af7d6433d53b24083e2219fa0",
"canvaskit/canvaskit.js.symbols": "48c83a2ce573d9692e8d970e288d75f7",
"canvaskit/canvaskit.wasm": "1f237a213d7370cf95f443d896176460",
"canvaskit/chromium/canvaskit.js": "87325e67bf77a9b483250e1fb1b54677",
"canvaskit/chromium/canvaskit.js.symbols": "a012ed99ccba193cf96bb2643003f6fc",
"canvaskit/chromium/canvaskit.wasm": "b1ac05b29c127d86df4bcfbf50dd902a",
"canvaskit/skwasm.js": "9fa2ffe90a40d062dd2343c7b84caf01",
"canvaskit/skwasm.js.symbols": "262f4827a1317abb59d71d6c587a93e2",
"canvaskit/skwasm.wasm": "9f0c0c02b82a910d12ce0543ec130e60",
"canvaskit/skwasm.worker.js": "bfb704a6c714a75da9ef320991e88b03",
"favicon.png": "68d70a7f689185f1156029565dd193eb",
"flutter.js": "f31737fb005cd3a3c6bd9355efd33061",
"flutter_bootstrap.js": "9ad1a848a9b8b5788aa4c11f6e4bffe9",
"icons/Icon-512.png": "68d70a7f689185f1156029565dd193eb",
"icons/Icon-maskable-192.png": "68d70a7f689185f1156029565dd193eb",
"icons/Icon-maskable-512.png": "68d70a7f689185f1156029565dd193eb",
"index.html": "fef819cea1edce9056b0c6434b97d05d",
"/": "fef819cea1edce9056b0c6434b97d05d",
"main.dart.js": "42d7f7568af84f80d542f8740c569599",
"manifest.json": "8284a976a6a03b705d735e4d96e2eaf1",
"version.json": "a568cdb30152705d8b44dbe8238535e8"};
// The application shell files that are downloaded before a service worker can
// start.
const CORE = ["main.dart.js",
"index.html",
"flutter_bootstrap.js",
"assets/AssetManifest.bin.json",
"assets/FontManifest.json"];

// During install, the TEMP cache is populated with the application shell files.
self.addEventListener("install", (event) => {
  self.skipWaiting();
  return event.waitUntil(
    caches.open(TEMP).then((cache) => {
      return cache.addAll(
        CORE.map((value) => new Request(value, {'cache': 'reload'})));
    })
  );
});
// During activate, the cache is populated with the temp files downloaded in
// install. If this service worker is upgrading from one with a saved
// MANIFEST, then use this to retain unchanged resource files.
self.addEventListener("activate", function(event) {
  return event.waitUntil(async function() {
    try {
      var contentCache = await caches.open(CACHE_NAME);
      var tempCache = await caches.open(TEMP);
      var manifestCache = await caches.open(MANIFEST);
      var manifest = await manifestCache.match('manifest');
      // When there is no prior manifest, clear the entire cache.
      if (!manifest) {
        await caches.delete(CACHE_NAME);
        contentCache = await caches.open(CACHE_NAME);
        for (var request of await tempCache.keys()) {
          var response = await tempCache.match(request);
          await contentCache.put(request, response);
        }
        await caches.delete(TEMP);
        // Save the manifest to make future upgrades efficient.
        await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
        // Claim client to enable caching on first launch
        self.clients.claim();
        return;
      }
      var oldManifest = await manifest.json();
      var origin = self.location.origin;
      for (var request of await contentCache.keys()) {
        var key = request.url.substring(origin.length + 1);
        if (key == "") {
          key = "/";
        }
        // If a resource from the old manifest is not in the new cache, or if
        // the MD5 sum has changed, delete it. Otherwise the resource is left
        // in the cache and can be reused by the new service worker.
        if (!RESOURCES[key] || RESOURCES[key] != oldManifest[key]) {
          await contentCache.delete(request);
        }
      }
      // Populate the cache with the app shell TEMP files, potentially overwriting
      // cache files preserved above.
      for (var request of await tempCache.keys()) {
        var response = await tempCache.match(request);
        await contentCache.put(request, response);
      }
      await caches.delete(TEMP);
      // Save the manifest to make future upgrades efficient.
      await manifestCache.put('manifest', new Response(JSON.stringify(RESOURCES)));
      // Claim client to enable caching on first launch
      self.clients.claim();
      return;
    } catch (err) {
      // On an unhandled exception the state of the cache cannot be guaranteed.
      console.error('Failed to upgrade service worker: ' + err);
      await caches.delete(CACHE_NAME);
      await caches.delete(TEMP);
      await caches.delete(MANIFEST);
    }
  }());
});
// The fetch handler redirects requests for RESOURCE files to the service
// worker cache.
self.addEventListener("fetch", (event) => {
  if (event.request.method !== 'GET') {
    return;
  }
  var origin = self.location.origin;
  var key = event.request.url.substring(origin.length + 1);
  // Redirect URLs to the index.html
  if (key.indexOf('?v=') != -1) {
    key = key.split('?v=')[0];
  }
  if (event.request.url == origin || event.request.url.startsWith(origin + '/#') || key == '') {
    key = '/';
  }
  // If the URL is not the RESOURCE list then return to signal that the
  // browser should take over.
  if (!RESOURCES[key]) {
    return;
  }
  // If the URL is the index.html, perform an online-first request.
  if (key == '/') {
    return onlineFirst(event);
  }
  event.respondWith(caches.open(CACHE_NAME)
    .then((cache) =>  {
      return cache.match(event.request).then((response) => {
        // Either respond with the cached resource, or perform a fetch and
        // lazily populate the cache only if the resource was successfully fetched.
        return response || fetch(event.request).then((response) => {
          if (response && Boolean(response.ok)) {
            cache.put(event.request, response.clone());
          }
          return response;
        });
      })
    })
  );
});
self.addEventListener('message', (event) => {
  // SkipWaiting can be used to immediately activate a waiting service worker.
  // This will also require a page refresh triggered by the main worker.
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
    return;
  }
  if (event.data === 'downloadOffline') {
    downloadOffline();
    return;
  }
});
// Download offline will check the RESOURCES for all files not in the cache
// and populate them.
async function downloadOffline() {
  var resources = [];
  var contentCache = await caches.open(CACHE_NAME);
  var currentContent = {};
  for (var request of await contentCache.keys()) {
    var key = request.url.substring(origin.length + 1);
    if (key == "") {
      key = "/";
    }
    currentContent[key] = true;
  }
  for (var resourceKey of Object.keys(RESOURCES)) {
    if (!currentContent[resourceKey]) {
      resources.push(resourceKey);
    }
  }
  return contentCache.addAll(resources);
}
// Attempt to download the resource online before falling back to
// the offline cache.
function onlineFirst(event) {
  return event.respondWith(
    fetch(event.request).then((response) => {
      return caches.open(CACHE_NAME).then((cache) => {
        cache.put(event.request, response.clone());
        return response;
      });
    }).catch((error) => {
      return caches.open(CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          if (response != null) {
            return response;
          }
          throw error;
        });
      });
    })
  );
}
