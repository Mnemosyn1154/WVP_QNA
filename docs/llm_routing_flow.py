#!/usr/bin/env python3
"""
Generate LLM Routing Flow Diagram
This creates a visual representation of the multi-LLM routing logic
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import matplotlib.lines as mlines

# Create figure and axis
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(0, 10)
ax.axis('off')

# Define colors
color_input = '#E8F5E9'
color_gemini = '#E3F2FD'
color_claude = '#FCE4EC'
color_decision = '#FFF9C4'
color_process = '#F3E5F5'
color_output = '#E0F2F1'

# Title
ax.text(7, 9.5, 'Multi-LLM Routing Architecture', fontsize=20, 
        fontweight='bold', ha='center')

# User Input
user_input = FancyBboxPatch((5.5, 8.2), 3, 0.8, 
                           boxstyle="round,pad=0.1",
                           facecolor=color_input, 
                           edgecolor='black', linewidth=2)
ax.add_patch(user_input)
ax.text(7, 8.6, 'User Query', fontsize=12, ha='center', fontweight='bold')

# Query Analysis
query_analysis = FancyBboxPatch((5, 6.8), 4, 0.8,
                               boxstyle="round,pad=0.1",
                               facecolor=color_decision,
                               edgecolor='black', linewidth=2)
ax.add_patch(query_analysis)
ax.text(7, 7.2, 'Query Analysis', fontsize=12, ha='center', fontweight='bold')

# Decision branches
# Gemini path
gemini_box = Rectangle((1, 4.5), 3, 1.8, 
                      facecolor=color_gemini, 
                      edgecolor='blue', linewidth=2)
ax.add_patch(gemini_box)
ax.text(2.5, 5.8, 'Gemini 1.5 Flash', fontsize=11, ha='center', fontweight='bold')
ax.text(2.5, 5.4, '• Simple queries', fontsize=9, ha='center')
ax.text(2.5, 5.1, '• Text-based PDFs', fontsize=9, ha='center')
ax.text(2.5, 4.8, '• Cost: $0.075/1M', fontsize=9, ha='center')

# Claude path
claude_box = Rectangle((10, 4.5), 3, 1.8,
                      facecolor=color_claude,
                      edgecolor='red', linewidth=2)
ax.add_patch(claude_box)
ax.text(11.5, 5.8, 'Claude 3.5 Sonnet', fontsize=11, ha='center', fontweight='bold')
ax.text(11.5, 5.4, '• Comparisons', fontsize=9, ha='center')
ax.text(11.5, 5.1, '• Scanned PDFs', fontsize=9, ha='center')
ax.text(11.5, 4.8, '• Cost: $3.00/1M', fontsize=9, ha='center')

# Text extraction process
text_extract = Rectangle((0.5, 2.8), 4, 1,
                        facecolor=color_process,
                        edgecolor='purple', linewidth=1)
ax.add_patch(text_extract)
ax.text(2.5, 3.3, 'Text Extraction', fontsize=10, ha='center', fontweight='bold')

# PDF analysis
pdf_analysis = Rectangle((9.5, 2.8), 4, 1,
                        facecolor=color_process,
                        edgecolor='purple', linewidth=1)
ax.add_patch(pdf_analysis)
ax.text(11.5, 3.3, 'Direct PDF Analysis', fontsize=10, ha='center', fontweight='bold')

# Decision criteria boxes
criteria1 = Rectangle((5, 5.2), 4, 0.5,
                     facecolor='white',
                     edgecolor='gray', linewidth=1, linestyle='--')
ax.add_patch(criteria1)
ax.text(7, 5.45, 'Contains "비교"?', fontsize=9, ha='center', style='italic')

criteria2 = Rectangle((5, 4.6), 4, 0.5,
                     facecolor='white',
                     edgecolor='gray', linewidth=1, linestyle='--')
ax.add_patch(criteria2)
ax.text(7, 4.85, 'Scanned PDF?', fontsize=9, ha='center', style='italic')

# Quality check
quality_check = FancyBboxPatch((1.5, 1.8), 2, 0.6,
                              boxstyle="round,pad=0.05",
                              facecolor=color_decision,
                              edgecolor='orange', linewidth=1)
ax.add_patch(quality_check)
ax.text(2.5, 2.1, 'Text Quality?', fontsize=9, ha='center')

# Final output
output_box = FancyBboxPatch((5.5, 0.2), 3, 0.8,
                           boxstyle="round,pad=0.1",
                           facecolor=color_output,
                           edgecolor='black', linewidth=2)
ax.add_patch(output_box)
ax.text(7, 0.6, 'Response to User', fontsize=12, ha='center', fontweight='bold')

# Draw arrows
# User to Analysis
ax.arrow(7, 8.2, 0, -1.2, head_width=0.2, head_length=0.1, fc='black', ec='black')

# Analysis to Gemini
ax.arrow(6, 6.8, -2.3, -0.3, head_width=0.2, head_length=0.1, fc='blue', ec='blue')
ax.text(4.5, 6.3, 'Simple', fontsize=9, color='blue')

# Analysis to Claude
ax.arrow(8, 6.8, 2.3, -0.3, head_width=0.2, head_length=0.1, fc='red', ec='red')
ax.text(9.2, 6.3, 'Complex', fontsize=9, color='red')

# Gemini to Text extraction
ax.arrow(2.5, 4.5, 0, -0.6, head_width=0.2, head_length=0.1, fc='blue', ec='blue')

# Claude to PDF analysis
ax.arrow(11.5, 4.5, 0, -0.6, head_width=0.2, head_length=0.1, fc='red', ec='red')

# Text extraction to quality check
ax.arrow(2.5, 2.8, 0, -0.3, head_width=0.2, head_length=0.1, fc='purple', ec='purple')

# Quality check branches
# Good quality to output
ax.arrow(2.5, 1.8, 2.8, -0.9, head_width=0.2, head_length=0.1, fc='green', ec='green')
ax.text(3.5, 1.2, 'Good', fontsize=8, color='green')

# Poor quality to Claude (fallback)
ax.arrow(3.5, 2.1, 6.5, 1.5, head_width=0.2, head_length=0.1, 
         fc='orange', ec='orange', linestyle='--')
ax.text(6.5, 3, 'Fallback', fontsize=8, color='orange', rotation=15)

# PDF analysis to output
ax.arrow(11.5, 2.8, -2.8, -1.9, head_width=0.2, head_length=0.1, fc='red', ec='red')

# Add usage percentage annotations
ax.text(2.5, 6.5, '~70-80%', fontsize=10, ha='center', 
        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue'))
ax.text(11.5, 6.5, '~20-30%', fontsize=10, ha='center',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='lightpink'))

# Add cost comparison
cost_box = Rectangle((0.2, 0.2), 3.5, 1.2,
                    facecolor='lightyellow',
                    edgecolor='black', linewidth=1)
ax.add_patch(cost_box)
ax.text(1.95, 1.1, 'Cost Optimization', fontsize=10, ha='center', fontweight='bold')
ax.text(1.95, 0.7, '90% reduction for', fontsize=8, ha='center')
ax.text(1.95, 0.4, 'simple queries', fontsize=8, ha='center')

# Add legend
legend_elements = [
    mlines.Line2D([0], [0], color='blue', lw=2, label='Gemini Path'),
    mlines.Line2D([0], [0], color='red', lw=2, label='Claude Path'),
    mlines.Line2D([0], [0], color='orange', lw=2, linestyle='--', label='Fallback'),
    patches.Patch(facecolor=color_decision, label='Decision Point'),
    patches.Patch(facecolor=color_process, label='Processing')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

# Save the diagram
plt.tight_layout()
plt.savefig('docs/llm_routing_flow.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.savefig('docs/llm_routing_flow.pdf', bbox_inches='tight', 
            facecolor='white', edgecolor='none')

print("LLM routing flow diagrams saved to:")
print("- docs/llm_routing_flow.png")
print("- docs/llm_routing_flow.pdf")