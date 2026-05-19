import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import binom

class BayesianQualityAI:
    def __init__(self, root):
        self.root = root
        self.root.title("HUE - Bayesian Quality Analyzer V2")
        self.root.geometry("1100x700")
        self.root.configure(bg="#121212")

        self.accent_color = "#00ADB5" 
        self.bg_card = "#1E1E1E"
        self.text_color = "#EEEEEE"

        header = tk.Frame(self.root, bg=self.bg_card, height=70)
        header.pack(fill="x", side="top", pady=(0, 2))
        
        title_label = tk.Label(header, text="BAYESIAN QUALITY CONTROL SYSTEM", 
                               bg=self.bg_card, fg=self.accent_color, 
                               font=("Verdana", 20, "bold"))
        title_label.pack(pady=15)
        main_container = tk.Frame(self.root, bg="#121212")
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        input_frame = tk.Frame(main_container, bg=self.bg_card, padx=25, pady=25)
        input_frame.place(relx=0, rely=0, relwidth=0.35, relheight=1)

        tk.Label(input_frame, text="INPUT PARAMETERS", bg=self.bg_card, 
                 fg=self.accent_color, font=("Verdana", 12, "bold")).pack(pady=(0, 20))

        self.entries = {}
        fields = [
            ("Sample Size (n)", "entry_total"),
            ("Expected Defect Rate (%)", "entry_rate"),
            ("Detected Faults (k)", "entry_detected")
        ]

        for label_text, var_name in fields:
            tk.Label(input_frame, text=label_text, bg=self.bg_card, 
                     fg=self.text_color, font=("Verdana", 10)).pack(anchor="w")
            entry = tk.Entry(input_frame, font=("Verdana", 12), bg="#333333", 
                             fg="white", insertbackground="white", relief="flat")
            entry.pack(fill="x", pady=(5, 15))
            self.entries[var_name] = entry

        self.btn_run = tk.Button(input_frame, text="RUN BAYESIAN ANALYSIS", 
                                 command=self.apply_bayes, bg=self.accent_color, 
                                 fg="#222831", font=("Verdana", 12, "bold"), 
                                 relief="flat", cursor="hand2")
        self.btn_run.pack(fill="x", pady=25)

        self.res_lbl = tk.Label(input_frame, text="System Ready", 
                                   bg=self.bg_card, fg="#888888", font=("Verdana", 10, "italic"))
        self.res_lbl.pack()

        display_frame = tk.Frame(main_container, bg=self.bg_card, padx=20, pady=20)
        display_frame.place(relx=0.38, rely=0, relwidth=0.62, relheight=1)

        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor(self.bg_card)
        self.canvas = FigureCanvasTkAgg(self.fig, master=display_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def apply_bayes(self):
        try:
            raw_n = self.entries["entry_total"].get()
            raw_rate = self.entries["entry_rate"].get()
            raw_k = self.entries["entry_detected"].get()

            if not raw_n or not raw_rate or not raw_k:
                messagebox.showerror("Input Error", "All fields must be filled!")
                return

            n = int(raw_n)
            p_healthy = float(raw_rate) / 100
            k = int(raw_k)

            if n <= 0:
                messagebox.showerror("Logical Error", "Sample size (n) must be greater than 0!")
                return
            if k > n:
                messagebox.showerror("Logical Error", "Detected faults (k) cannot be more than sample size (n)!")
                return
            if p_healthy < 0 or p_healthy > 1:
                messagebox.showerror("Logical Error", "Defect rate must be between 0 and 100%!")
                return
            prior_broken = 0.10
            prior_healthy = 0.90
            
            p_if_broken = max(0.10, p_healthy * 2) 
            
            likelihood_broken = binom.pmf(k, n, p_if_broken)
            likelihood_healthy = binom.pmf(k, n, p_healthy)

            evidence = (likelihood_broken * prior_broken) + (likelihood_healthy * prior_healthy)
            
            if evidence == 0:
                posterior_broken = 1.0 if k/n > p_healthy else 0.0
            else:
                posterior_broken = (likelihood_broken * prior_broken) / evidence

            if posterior_broken > 0.5:
                res_text = "STATUS: CRITICAL (Machine Fault Likely)"
                color = "#FF4B2B"
            else:
                res_text = "STATUS: OPTIMAL (Healthy Process)"
                color = "#00FFAB"

            self.res_lbl.config(text=f"{res_text}\nConfidence in Fault: {posterior_broken:.2%}", fg=color)
            self.update_chart(posterior_broken)

        except ValueError:
            messagebox.showerror("Type Error", "Please enter valid numbers!")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def update_chart(self, prob_broken):
        self.ax.clear()
        prob_healthy = 1 - prob_broken
        labels = ['Healthy State', 'Broken State']
        colors = [self.accent_color, "#FF4B2B"]
        
        self.ax.pie([prob_healthy, prob_broken], labels=labels, 
                    autopct='%1.1f%%', colors=colors, startangle=90,
                    wedgeprops={'width': 0.4, 'edgecolor': self.bg_card},
                    textprops={'color':"w"})
        
        self.ax.set_title("BAYESIAN PROBABILITY ANALYSIS", color="white", fontname="Verdana", fontsize=12)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = BayesianQualityAI(root)
    root.mainloop()