import 'package:flutter/material.dart';
import '../models/camp_model.dart';

class ComparisonScreen extends StatelessWidget {
  final List<Camp> camps;
  final Function(String) onRemoveCamp;

  const ComparisonScreen({
    Key? key,
    required this.camps,
    required this.onRemoveCamp,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        title: const Text(
          'Side-by-Side Camp Comparison',
          style: TextStyle(
            color: Color(0xFF1A1A2E),
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Color(0xFF1A1A2E)),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: camps.isEmpty
          ? const Center(
              child: Text(
                'No camps selected for comparison.\nSelect camps using the "Compare" checkbox.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Color(0xFF5A6A7C), fontSize: 14),
              ),
            )
          : SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: SingleChildScrollView(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: DataTable(
                    headingRowHeight: 70,
                    dataRowMaxHeight: 60,
                    columns: [
                      const DataColumn(
                        label: Text(
                          'FEATURE',
                          style: TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF8A9AA8)),
                        ),
                      ),
                      ...camps.map(
                        (camp) => DataColumn(
                          label: Container(
                            constraints: const BoxConstraints(maxWidth: 160),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Text(
                                    camp.name,
                                    style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFFFF6B6B)),
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                IconButton(
                                  icon: const Icon(Icons.close, size: 16, color: Colors.grey),
                                  onPressed: () => onRemoveCamp(camp.id),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                    rows: [
                      _buildRow('Location', camps.map((c) => '${c.city}, ${c.state}').toList()),
                      _buildRow('Weekly Price', camps.map((c) => c.price != null ? '\$${c.price!.toInt()} / wk' : 'On request').toList()),
                      _buildRow('Age Range', camps.map((c) => c.ageMin != null && c.ageMax != null ? '${c.ageMin}–${c.ageMax} yrs' : 'On request').toList()),
                      _buildRow('Camp Type', camps.map((c) => c.type).toList()),
                      _buildRow('Theme & Focus', camps.map((c) => c.theme).toList()),
                      _buildRow('Early Care (Before 8 AM)', camps.map((c) => c.beforeCare == true ? '✓ Yes' : (c.beforeCare == false ? '✗ No' : '—')).toList()),
                      _buildRow('Late Care (After 5 PM)', camps.map((c) => c.afterCare == true ? '✓ Yes' : (c.afterCare == false ? '✗ No' : '—')).toList()),
                      _buildRow('Shuttle Bus', camps.map((c) => c.shuttle == true ? '✓ Yes' : (c.shuttle == false ? '✗ No' : '—')).toList()),
                      _buildRow('Active Weeks', camps.map((c) => c.weeks.isNotEmpty ? '${c.weeks.length} Weeks' : 'On request').toList()),
                    ],
                  ),
                ),
              ),
            ),
    );
  }

  DataRow _buildRow(String featureTitle, List<String> values) {
    return DataRow(
      cells: [
        DataCell(
          Text(
            featureTitle,
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Color(0xFF2C3E50)),
          ),
        ),
        ...values.map(
          (val) => DataCell(
            Text(
              val,
              style: const TextStyle(fontSize: 13, color: Color(0xFF5A6A7C)),
            ),
          ),
        ),
      ],
    );
  }
}
