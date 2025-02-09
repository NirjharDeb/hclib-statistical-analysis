import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Initialize dictionaries to store data for plotting and t-tests
means_dict = {}
data_samples = {}

def tTest(nodes, folder_name, variant):
    """
    Reads the performance data for a given variant and number of nodes.
    """
    filepath = os.path.join(folder_name, variant, f"{variant}_{nodes}.txt")
    
    try:
        data_sample = pd.read_csv(filepath, header=None).squeeze()
        if data_sample.empty:
            print(f"Warning: File {filepath} is empty.")
            return None
    except FileNotFoundError:
        print(f"Data file for {nodes} nodes not found in variant '{variant}' at path {filepath}.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: No data to parse in file {filepath}. It may be empty.")
        return None

    return data_sample

def run_tests(folder_name, node_counts, pdf_file, plot_filename, baseline_variant=None):
    global means_dict, data_samples

    # Initialize document and styles
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Register fonts and choose a clean font for the document
    try:
        pdfmetrics.registerFont(TTFont('HelveticaNeue', 'HelveticaNeue.ttf'))
        font_name = 'HelveticaNeue'
    except:
        font_name = 'Helvetica'

    title_style = styles['Title']
    title_style.fontName = font_name
    title_style.fontSize = 14
    title_style.spaceAfter = 10

    normal_style = styles['Normal']
    normal_style.fontName = font_name
    normal_style.fontSize = 11

    # Detect algorithm variants
    variant_dirs = [d for d in os.listdir(folder_name) if os.path.isdir(os.path.join(folder_name, d))]
    if len(variant_dirs) < 2:
        print(f"Insufficient variant directories found in {folder_name}. At least two are required.")
        return

    # Check if the specified baseline_variant exists; if not, default to the first variant found.
    if baseline_variant is None or baseline_variant not in variant_dirs:
        baseline_variant = variant_dirs[0]
        print(f"Baseline variant not specified or not found. Defaulting to: {baseline_variant}")
    else:
        print(f"Using baseline variant: {baseline_variant}")

    # Initialize data structures
    for variant in variant_dirs:
        means_dict[variant] = []
        data_samples[variant] = {}

    # Collect data samples and means for each variant
    for nodes in node_counts:
        for variant in variant_dirs:
            data_sample = tTest(nodes, folder_name, variant)
            if data_sample is not None:
                data_samples[variant][nodes] = data_sample
                mean_laptime = data_sample.mean()
                means_dict[variant].append(mean_laptime)
            else:
                means_dict[variant].append(None)

    # 1. Graph Section - Speedup vs Number of Nodes
    elements.append(Paragraph("Graph: Speedup vs Number of Nodes", title_style))
    
    # Plot speedup for each variant compared to the baseline
    plt.figure(figsize=(6, 4))
    color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for idx, variant in enumerate(variant_dirs):
        speedups = []
        filtered_nodes = []
        for i, nodes in enumerate(node_counts):
            baseline_mean = means_dict[baseline_variant][i]
            variant_mean = means_dict[variant][i]
            # Ensure both baseline and variant data exist and avoid division by zero.
            if baseline_mean is not None and variant_mean is not None and variant_mean != 0:
                speedup = baseline_mean / variant_mean
                speedups.append(speedup)
                filtered_nodes.append(nodes)
        if speedups:
            plt.plot(filtered_nodes, speedups, label=variant, marker='o', linestyle='-',
                     color=color_palette[idx % len(color_palette)])
    
    plt.xlabel("Number of Nodes (each with 24 PEs)")
    plt.ylabel("Speedup (Baseline = 1)")
    plt.title(f"Speedup vs Number of Nodes (Baseline: {baseline_variant})")
    plt.legend()
    plt.grid(True, linestyle='--', linewidth=0.5, color='grey')
    
    # Set only the y-axis to start at 0
    plt.ylim(bottom=0)
    
    plt.tight_layout()

    # Save the plot as a high-resolution image and add it to the PDF
    plt.savefig(plot_filename, dpi=300)
    elements.append(Image(plot_filename, width=6 * inch, height=4 * inch))
    elements.append(Spacer(1, 12))

    # 2. Average Percentage Differences Section (relative to baseline_variant)
    elements.append(Paragraph(f"Average Percentage Differences (Baseline: {baseline_variant})", title_style))
    
    for variant in variant_dirs:
        if variant == baseline_variant:
            continue  # Skip comparing the baseline to itself

        perc_diffs = []
        for idx, nodes in enumerate(node_counts):
            baseline_mean = means_dict[baseline_variant][idx]
            comp_mean = means_dict[variant][idx]
            if baseline_mean is not None and comp_mean is not None and baseline_mean != 0:
                perc_diff = ((comp_mean - baseline_mean) / baseline_mean) * 100
                perc_diffs.append(perc_diff)
        if perc_diffs:
            avg_perc_diff = sum(perc_diffs) / len(perc_diffs)
            if avg_perc_diff > 0:
                diff_desc = f"on average {avg_perc_diff:.2f}% higher"
            elif avg_perc_diff < 0:
                diff_desc = f"on average {abs(avg_perc_diff):.2f}% lower"
            else:
                diff_desc = "with no difference"
        else:
            diff_desc = "Insufficient data to compute average percentage difference."
        
        text = (f"Compared to baseline variant '{baseline_variant}', variant '{variant}' has lap times that are {diff_desc}.")
        elements.append(Paragraph(text, normal_style))
        elements.append(Spacer(1, 8))

    # 3. Two-Sample T-Tests Section (pairwise comparisons)
    elements.append(Paragraph("Two-Sample T-Tests", title_style))

    # Generate a table for each pairwise comparison
    for i in range(len(variant_dirs)):
        for j in range(i + 1, len(variant_dirs)):
            baseline_v = variant_dirs[i]
            comparison_v = variant_dirs[j]

            # Add null hypothesis statement
            hypothesis_text = (
                f"Null Hypothesis: There is no significant difference in mean lap times between "
                f"'{baseline_v}' and '{comparison_v}' variants."
            )
            elements.append(Paragraph(hypothesis_text, normal_style))
            elements.append(Spacer(1, 8))

            # Initialize table data
            table_data = [["Nodes", "t-statistic", "p-value", "Conclusion"]]
            
            for nodes in node_counts:
                if (nodes in data_samples[baseline_v] and nodes in data_samples[comparison_v]):
                    sample1 = data_samples[baseline_v][nodes]
                    sample2 = data_samples[comparison_v][nodes]

                    # Check if samples are valid for t-test
                    if len(sample1) >= 2 and len(sample2) >= 2 and sample1.std() != 0 and sample2.std() != 0:
                        t_stat, p_value = stats.ttest_ind(sample1, sample2, equal_var=False)
                        t_stat_formatted = f"{t_stat:.2e}"
                        p_value_formatted = f"{p_value:.2e}"
                        conclusion = "Significant" if p_value < 0.05 else "Not Significant"
                    else:
                        t_stat_formatted, p_value_formatted, conclusion = "N/A", "N/A", "Insufficient data"
                else:
                    t_stat_formatted, p_value_formatted, conclusion = "N/A", "N/A", "Data missing"
                
                table_data.append([str(nodes), t_stat_formatted, p_value_formatted, conclusion])

            # Create and style the table
            table = Table(table_data, colWidths=[1.2 * inch, 1.5 * inch, 1.5 * inch, 1.8 * inch])
            table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.95, 0.95, 0.95)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 12))

    # Build PDF
    doc.build(elements)
    print(f"Hypothesis test results, average percentage differences, and graph have been saved to {pdf_file}")

# Example usage
if __name__ == "__main__":
    folder_name = "../toposort_global_spring_2025_500000"
    node_counts = [1, 2, 4, 8, 16, 32]
    pdf_file = "toposort_initiate_global_done_analysis_500000.pdf"
    plot_filename = "toposort_initiate_global_done_graph_500000.png"
    baseline_variant = "original_toposort"
    run_tests(folder_name, node_counts, pdf_file, plot_filename, baseline_variant)
