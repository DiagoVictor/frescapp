import 'package:flutter/material.dart';
import 'package:flutter_pdfview/flutter_pdfview.dart';

class PDFViewerScreen extends StatelessWidget {
  final String url;

  const PDFViewerScreen({super.key, required this.url});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PDF Viewer'),
      ),
      body: Center(
        child: PDFView(
          filePath: url,
        ),
      ),
    );
  }
}
