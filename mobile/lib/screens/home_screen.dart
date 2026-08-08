import 'package:flutter/material.dart';
import '../models/camp_model.dart';
import '../services/camp_repository.dart';
import '../widgets/camp_card.dart';
import '../widgets/paywall_modal.dart';
import 'camp_detail_screen.dart';
import 'comparison_screen.dart';

class HomeScreen extends StatefulWidget {
  final CampRepository repository;

  const HomeScreen({super.key, required this.repository});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final FilterOptions _filters = FilterOptions();
  List<Camp> _filteredCamps = [];
  final List<String> _comparedCampIds = [];
  bool _isMapView = false;
  bool _isProUser = false;

  void _openPaywall(String featureName) async {
    final result = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => PaywallModal(featureTrigger: featureName),
    );
    if (result == true) {
      setState(() {
        _isProUser = true;
      });
    }
  }

  @override
  void initState() {
    super.initState();
    _applyFilters();
  }

  void _applyFilters() {
    setState(() {
      _filteredCamps = widget.repository.filterCamps(_filters);
    });
  }

  void _toggleCompare(String campId) {
    setState(() {
      if (_comparedCampIds.contains(campId)) {
        _comparedCampIds.remove(campId);
      } else {
        if (_comparedCampIds.length >= 3) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('You can compare up to 3 camps at a time.')),
          );
        } else {
          _comparedCampIds.add(campId);
        }
      }
    });
  }

  void _openFilterModal() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setModalState) {
            return Padding(
              padding: EdgeInsets.only(
                top: 20,
                left: 20,
                right: 20,
                bottom: MediaQuery.of(context).viewInsets.bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'Filter Camps',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1A1A2E)),
                        ),
                        TextButton(
                          onPressed: () {
                            setModalState(() {
                              _filters.childAge = 10;
                              _filters.isSiblingMode = false;
                              _filters.season = 'all';
                              _filters.campType = 'all';
                              _filters.theme = 'all';
                              _filters.sessionWeek = 0;
                              _filters.requireBeforeCare = false;
                              _filters.requireAfterCare = false;
                              _filters.requireShuttle = false;
                            });
                            _applyFilters();
                          },
                          child: const Text('Reset All', style: TextStyle(color: Color(0xFFFF6B6B))),
                        ),
                      ],
                    ),
                    const Divider(),

                    // Child's Age Slider
                    Text('Child Age: ${_filters.childAge} yrs', style: const TextStyle(fontWeight: FontWeight.bold)),
                    Slider(
                      value: _filters.childAge.toDouble(),
                      min: 2,
                      max: 18,
                      divisions: 16,
                      activeColor: const Color(0xFFFF6B6B),
                      label: '${_filters.childAge} yrs',
                      onChanged: (val) {
                        setModalState(() => _filters.childAge = val.round());
                        _applyFilters();
                      },
                    ),

                    // Multi-Child Sibling Mode Toggle (Pro Feature)
                    SwitchListTile(
                      title: Row(
                        children: [
                          const Text('👨‍👩‍👧‍👦 Multi-Child / Sibling Mode', style: TextStyle(fontWeight: FontWeight.w600)),
                          const SizedBox(width: 6),
                          if (!_isProUser)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(color: const Color(0xFFFFD700), borderRadius: BorderRadius.circular(6)),
                              child: const Text('PRO', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.black)),
                            ),
                        ],
                      ),
                      subtitle: const Text('Find camps suitable for 2 children'),
                      value: _filters.isSiblingMode,
                      activeThumbColor: const Color(0xFF4ECDC4),
                      onChanged: (val) {
                        if (val && !_isProUser) {
                          _openPaywall('Sibling Mode');
                          return;
                        }
                        setModalState(() => _filters.isSiblingMode = val);
                        _applyFilters();
                      },
                    ),

                    if (_filters.isSiblingMode) ...[
                      Text('Child 2 Age: ${_filters.child2Age} yrs', style: const TextStyle(fontWeight: FontWeight.bold)),
                      Slider(
                        value: _filters.child2Age.toDouble(),
                        min: 2,
                        max: 18,
                        divisions: 16,
                        activeColor: const Color(0xFF4ECDC4),
                        onChanged: (val) {
                          setModalState(() => _filters.child2Age = val.round());
                          _applyFilters();
                        },
                      ),
                    ],

                    const SizedBox(height: 12),

                    // Season Filter Pills
                    const Text('Season', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 8,
                      children: [
                        _buildChoiceChip('All Seasons', 'all', _filters.season, (val) {
                          setModalState(() => _filters.season = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('🌞 Summer', 'summer', _filters.season, (val) {
                          setModalState(() => _filters.season = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('❄️ Winter Camp', 'winter', _filters.season, (val) {
                          setModalState(() => _filters.season = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('🌸 Spring Break', 'spring', _filters.season, (val) {
                          setModalState(() => _filters.season = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('🍂 Fall', 'fall', _filters.season, (val) {
                          setModalState(() => _filters.season = val);
                          _applyFilters();
                        }),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // Theme & Focus
                    const Text('Theme & Focus', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 8,
                      children: [
                        _buildChoiceChip('All Themes', 'all', _filters.theme, (val) {
                          setModalState(() => _filters.theme = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('🔬 STEM & Code', 'STEM', _filters.theme, (val) {
                          setModalState(() => _filters.theme = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('⚽ Sports', 'Sports', _filters.theme, (val) {
                          setModalState(() => _filters.theme = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('🎨 Arts & Drama', 'Arts', _filters.theme, (val) {
                          setModalState(() => _filters.theme = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('🌲 Outdoor', 'Outdoor', _filters.theme, (val) {
                          setModalState(() => _filters.theme = val);
                          _applyFilters();
                        }),
                        _buildChoiceChip('🏛️ City-Run', 'city', _filters.theme, (val) {
                          setModalState(() {
                            _filters.theme = val;
                            _filters.cityOnly = (val == 'city');
                          });
                          _applyFilters();
                        }),
                      ],
                    ),

                    const SizedBox(height: 16),

                    // Logistics Checks
                    CheckboxListTile(
                      title: const Text('🌅 Early Care (Before 8 AM)'),
                      value: _filters.requireBeforeCare,
                      onChanged: (val) {
                        setModalState(() => _filters.requireBeforeCare = val ?? false);
                        _applyFilters();
                      },
                    ),
                    CheckboxListTile(
                      title: const Text('🌆 Late Care (After 5 PM)'),
                      value: _filters.requireAfterCare,
                      onChanged: (val) {
                        setModalState(() => _filters.requireAfterCare = val ?? false);
                        _applyFilters();
                      },
                    ),
                    CheckboxListTile(
                      title: const Text('🚌 Shuttle Bus'),
                      value: _filters.requireShuttle,
                      onChanged: (val) {
                        setModalState(() => _filters.requireShuttle = val ?? false);
                        _applyFilters();
                      },
                    ),

                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFFF6B6B),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        ),
                        onPressed: () => Navigator.pop(context),
                        child: Text('Show ${_filteredCamps.length} Camps'),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildChoiceChip(String label, String value, String currentGroupValue, Function(String) onSelected) {
    final isSelected = currentGroupValue.toLowerCase() == value.toLowerCase();
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      selectedColor: const Color(0xFFFF6B6B),
      labelStyle: TextStyle(color: isSelected ? Colors.white : const Color(0xFF2C3E50), fontWeight: FontWeight.w600),
      onSelected: (_) => onSelected(value),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F6F9),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0.5,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFFFF6B6B).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.location_on, color: Color(0xFFFF6B6B), size: 20),
            ),
            const SizedBox(width: 8),
            const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'CampFind',
                  style: TextStyle(color: Color(0xFF1A1A2E), fontSize: 18, fontWeight: FontWeight.bold),
                ),
                Text(
                  'Summer · Winter · Spring · Fall Camps',
                  style: TextStyle(color: Color(0xFF8A9AA8), fontSize: 11),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(_isMapView ? Icons.list_alt : Icons.map, color: const Color(0xFF2C3E50)),
            onPressed: () {
              setState(() => _isMapView = !_isMapView);
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Search & Filter Header
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: 'Search ZIP (e.g. 92056), City, or Camp Name...',
                      hintStyle: const TextStyle(fontSize: 13, color: Color(0xFF8A9AA8)),
                      prefixIcon: const Icon(Icons.search, size: 20, color: Color(0xFF5A6A7C)),
                      filled: true,
                      fillColor: const Color(0xFFF4F6F9),
                      contentPadding: const EdgeInsets.symmetric(vertical: 0),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                    ),
                    onChanged: (val) {
                      _filters.searchQuery = val;
                      _applyFilters();
                    },
                  ),
                ),
                const SizedBox(width: 10),
                IconButton(
                  style: IconButton.styleFrom(
                    backgroundColor: const Color(0xFF4ECDC4).withValues(alpha: 0.15),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  icon: const Icon(Icons.tune, color: Color(0xFF3AB5AD)),
                  onPressed: _openFilterModal,
                ),
              ],
            ),
          ),

          // Count & Active Filter Indicator
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${_filteredCamps.length} Camps Available',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: Color(0xFF1A1A2E)),
                ),
                if (_filters.isSiblingMode)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: const Color(0xFF4ECDC4).withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Text('👨‍👩‍👧‍👦 Sibling Mode Active', style: TextStyle(fontSize: 11, color: Color(0xFF3AB5AD), fontWeight: FontWeight.bold)),
                  ),
              ],
            ),
          ),

          // List View or Map View
          Expanded(
            child: _filteredCamps.isEmpty
                ? const Center(
                    child: Text(
                      'No camps found matching your criteria.\nTry adjusting your filters.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Color(0xFF5A6A7C)),
                    ),
                  )
                : ListView.builder(
                    itemCount: _filteredCamps.length,
                    itemBuilder: (context, index) {
                      final camp = _filteredCamps[index];
                      final isFav = widget.repository.isFavorite(camp.id);
                      final isComp = _comparedCampIds.contains(camp.id);

                      return CampCard(
                        camp: camp,
                        isFavorite: isFav,
                        onFavoriteTap: () async {
                          await widget.repository.toggleFavorite(camp.id);
                          setState(() {});
                        },
                        onCompareTap: () => _toggleCompare(camp.id),
                        isSelectedForCompare: isComp,
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => CampDetailScreen(
                                camp: camp,
                                isFavorite: isFav,
                                onFavoriteTap: () async {
                                  await widget.repository.toggleFavorite(camp.id);
                                  setState(() {});
                                },
                              ),
                            ),
                          );
                        },
                      );
                    },
                  ),
          ),
        ],
      ),

      // Comparison Floating Bar
      floatingActionButton: _comparedCampIds.isNotEmpty
          ? FloatingActionButton.extended(
              backgroundColor: const Color(0xFFFF6B6B),
              icon: const Icon(Icons.compare_arrows, color: Colors.white),
              label: Text(
                'Compare ${_comparedCampIds.length} Camps',
                style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
              ),
              onPressed: () {
                final selectedCamps = widget.repository.allCamps
                    .where((c) => _comparedCampIds.contains(c.id))
                    .toList();
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => ComparisonScreen(
                      camps: selectedCamps,
                      onRemoveCamp: (id) {
                        _toggleCompare(id);
                      },
                    ),
                  ),
                );
              },
            )
          : null,
    );
  }
}
