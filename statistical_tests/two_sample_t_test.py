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


def run_tests(folder_name, node_counts, pdf_file, plot_filename):
    global means_dict, data_samples

    # Initialize document and styles
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Register fonts
    try:
        pdfmetrics.registerFont(TTFont('HelveticaNeue', 'HelveticaNeue.ttf'))
        font_name = 'HelveticaNeue'
    except:
        font_name = 'Helvetica'

    # Detect algorithm variants
    variant_dirs = [d for d in os.listdir(folder_name) if os.path.isdir(os.path.join(folder_name, d))]
    if len(variant_dirs) < 2:
        print(f"Insufficient variant directories found in {folder_name}. At least two are required.")
        return

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

    # Plot mean lap times for all variants
    plt.figure(figsize=(6, 4))
    color_palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Modern color palette
    for idx, (variant, means) in enumerate(means_dict.items()):
        filtered_means = [m for m in means if m is not None]
        filtered_nodes = [node_counts[i] for i, m in enumerate(means) if m is not None]
        if filtered_means:
            plt.plot(filtered_nodes, filtered_means, label=variant, marker='o', linestyle='-',
                     color=color_palette[idx % len(color_palette)])
    plt.xlabel("Number of Nodes")
    plt.ylabel("Mean Lap Time (ms)")
    plt.title("Mean Lap Times for Algorithm Variants")
    plt.legend()
    plt.grid(True, linestyle='--', linewidth=0.5, color='grey')
    plt.tight_layout()

    # Save the plot as a high-resolution image and add it to the PDF before the tables
    plt.savefig(plot_filename, dpi=300)
    elements.append(Image(plot_filename, width=6 * inch, height=4 * inch))

    # Generate a table for each pairwise comparison
    for i in range(len(variant_dirs)):
        for j in range(i + 1, len(variant_dirs)):
            baseline_variant = variant_dirs[i]
            comparison_variant = variant_dirs[j]

            # Add null hypothesis statement
            hypothesis_text = (
                f"Null Hypothesis: There is no significant difference in mean lap times between "
                f"'{baseline_variant}' and '{comparison_variant}' variants."
            )
            elements.append(Paragraph(hypothesis_text, styles["Normal"]))
            elements.append(Spacer(1, 12))

            # Initialize table data
            table_data = [["Nodes", "t-statistic", "p-value", "Conclusion"]]
            
            for nodes in node_counts:
                if (nodes in data_samples[baseline_variant] and nodes in data_samples[comparison_variant]):
                    sample1 = data_samples[baseline_variant][nodes]
                    sample2 = data_samples[comparison_variant][nodes]

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
                ('FONTNAME', (0, 0), (-1, 0), font_name),
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
    print(f"Hypothesis test results and plot have been saved to {pdf_file}")



# Example usage for triangle counting algorithm variants (original, linear search, binary search)
if __name__ == "__main__":
    folder_name = "../triangle_counter_fall_2024"
    node_counts = [1, 2, 4, 8, 16]
    pdf_file = "triangle_counter_analysis.pdf"
    plot_filename = "triangle_counter_graph.png"
    run_tests(folder_name, node_counts, pdf_file, plot_filename)
