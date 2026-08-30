import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/camp_model.dart';
import '../services/camp_repository.dart';
import '../widgets/camp_card.dart';

import 'camp_detail_screen.dart';
import 'comparison_screen.dart';
import 'claim_camp_screen.dart';

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
  bool _showOnboardingTip = false;

  @override
  void initState() {
    super.initState();
    _applyFilters();
    _checkOnboardingTip();
  }

  Future<void> _checkOnboardingTip() async {
    final prefs = await SharedPreferences.getInstance();
    final hasSeen = prefs.getBool('seen_onboarding_guide_v1') ?? false;
    if (!hasSeen && mounted) {
      setState(() {
        _showOnboardingTip = true;
      });
    }
  }

  Future<void> _dismissOnboardingTip() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('seen_onboarding_guide_v1', true);
    if (mounted) {
      setState(() {
        _showOnboardingTip = false;
      });
    }
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

                    // Multi-Child Sibling Mode Toggle
                    SwitchListTile(
                      title: const Text('👨‍👩‍👧‍👦 Multi-Child / Sibling Mode', style: TextStyle(fontWeight: FontWeight.w600)),
                      subtitle: const Text('Find camps suitable for 2 children'),
                      value: _filters.isSiblingMode,
                      activeThumbColor: const Color(0xFF4ECDC4),
                      onChanged: (val) {
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

                    // Session Week Picker
                    const Text('Session Week', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: _buildDynamicWeekChips(setModalState),
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

  List<Widget> _buildDynamicWeekChips(StateSetter setModalState) {
    final season = _filters.season.toLowerCase();

    List<Map<String, dynamic>> options = [];

    if (season == 'spring') {
      options = [
        {'label': 'Any Spring Session', 'week': 0},
        {'label': '🌸 Week 1 (Mar 16–27)', 'week': 1},
        {'label': '🌸 Week 2 (Mar 30–Apr 10)', 'week': 2},
      ];
    } else if (season == 'fall') {
      options = [
        {'label': 'Any Fall Session', 'week': 0},
        {'label': '🍂 Fall Break (Oct 12–16)', 'week': 1},
        {'label': '🦃 Thanksgiving (Nov 23–27)', 'week': 2},
      ];
    } else if (season == 'winter') {
      options = [
        {'label': 'Any Winter Week', 'week': 0},
        {'label': '🎄 Christmas (Dec 22–26)', 'week': 1},
        {'label': '🎆 New Year (Dec 29–Jan 2)', 'week': 2},
        {'label': '❄️ Week 3 (Jan 5–9)', 'week': 3},
      ];
    } else if (season == 'summer') {
      options = [
        {'label': 'Any Summer Week', 'week': 0},
        {'label': 'Week 1 (Jun 2–13)', 'week': 1},
        {'label': 'Week 2 (Jun 16–27)', 'week': 2},
        {'label': 'Week 3 (Jun 30–Jul 11)', 'week': 3},
        {'label': 'Week 4 (Jul 14–25)', 'week': 4},
        {'label': 'Week 5 (Jul 28–Aug 8)', 'week': 5},
        {'label': 'Week 6 (Aug 11–22)', 'week': 6},
      ];
    } else {
      options = [
        {'label': 'Any Week', 'week': 0},
        for (int w = 1; w <= 8; w++) {'label': 'Week $w', 'week': w},
      ];
    }

    return options.map((opt) {
      final int weekVal = opt['week'] as int;
      final String label = opt['label'] as String;
      final bool isSelected = _filters.sessionWeek == weekVal;
      return ChoiceChip(
        label: Text(label),
        selected: isSelected,
        selectedColor: weekVal == 0 ? const Color(0xFFFF6B6B) : const Color(0xFF4ECDC4),
        labelStyle: TextStyle(
          color: isSelected ? Colors.white : const Color(0xFF2C3E50),
          fontWeight: FontWeight.w600,
        ),
        onSelected: (_) {
          setModalState(() => _filters.sessionWeek = weekVal);
          _applyFilters();
        },
      );
    }).toList();
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
            tooltip: 'For Camp Directors',
            icon: const Icon(Icons.storefront_outlined, color: Color(0xFF16A34A)),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const ClaimCampScreen(),
                ),
              );
            },
          ),
          IconButton(
            tooltip: 'Privacy Policy',
            icon: const Icon(Icons.privacy_tip_outlined, color: Color(0xFF64748B)),
            onPressed: () {
              launchUrl(
                Uri.parse('https://campfind-app.netlify.app/privacy.html'),
                mode: LaunchMode.externalApplication,
              );
            },
          ),
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

          // Welcome / Onboarding Walkthrough Banner
          if (_showOnboardingTip)
            Container(
              margin: const EdgeInsets.fromLTRB(16, 8, 16, 4),
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFFFFF9E6),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFFFD700).withValues(alpha: 0.8)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Row(
                        children: [
                          Icon(Icons.lightbulb_outline, color: Color(0xFFD97706), size: 20),
                          SizedBox(width: 6),
                          Text(
                            'Welcome to CampFind!',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                              color: Color(0xFF92400E),
                            ),
                          ),
                        ],
                      ),
                      GestureDetector(
                        onTap: _dismissOnboardingTip,
                        child: const Icon(Icons.close, size: 18, color: Color(0xFFB45309)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '• Filter by Age & Sibling Mode to find camps matching multiple kids.\n• Tap the Compare button on cards to compare up to 3 camps side-by-side.\n• Toggle the Map icon at the top right to explore camps by location.',
                    style: TextStyle(fontSize: 12, color: Color(0xFF78350F), height: 1.4),
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
                        onTap: () async {
                          final selectedWeek = await Navigator.push<int>(
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
                          if (selectedWeek != null && selectedWeek > 0) {
                            setState(() {
                              _filters.sessionWeek = selectedWeek;
                            });
                            _applyFilters();
                          }
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
