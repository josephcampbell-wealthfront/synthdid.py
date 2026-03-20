import matplotlib, matplotlib.pyplot as plt, numpy as np, pandas as pd, math

class Plots:
    def plot_outcomes(self, times = None, time_title_cb = int, labels=None, wtplot=True, axlimit_zero=False):
        # matplotlib.use('Agg')
        sdid_weights = self.weights
        lambda_wg = sdid_weights["lambda"]
        omega_wg = sdid_weights["omega"]
        table_result = self.att_info
        N0s, T0s = table_result.N0, table_result.T0
        if times is None:
            times = table_result.time
        if labels is None:
            labels = ['Control','Treatment']

        Y_setups = self.Y_betas
        t_span = np.sort(np.unique(self.data_ref.time))
        # plots = {}
        plots = []
        for i, time in enumerate(times):
            omega_hat = omega_wg[i]
            lambda_hat = lambda_wg[i]
            N0, T0 = N0s[i], T0s[i]
            Y_year = np.array(Y_setups[i])
            Y_t = np.mean(Y_year[N0:, :], axis=0)
            Y_c = Y_year[:N0, :]
            n_features = Y_c.shape[0]
            Y_sdid_traj = np.dot(omega_hat, Y_c)

            values_traj = np.concatenate((Y_sdid_traj, Y_t))

            plot_y_min = values_traj.min()
            plot_y_max = values_traj.max()
            plot_height = plot_y_max - plot_y_min
            base_plot = plot_y_min - plot_height / 5 
            if axlimit_zero:
                base_plot = 0

            trajectory = pd.DataFrame(
                {
                    "time": t_span,
                    'control': Y_sdid_traj,
                    'treatment': Y_t
                }
            )

            fig, ax = plt.subplots()
            ax.plot("time", "control", label=labels[0], data=trajectory, linestyle="--")
            ax.plot("time", "treatment", label=labels[1], data=trajectory)
            ax.legend(loc='upper right', fontsize=10, frameon=False)
            if base_plot < 0 and plot_y_max > 0:
                ax.axhline(y=0, color="grey", linestyle="--", lw=.8, alpha=.3)
            if wtplot:
                # Secondary y-axis for lambda weights, matching Stata:
                # ylim(0, 3) so lambda=1.0 appears at 1/3 of chart height (bottom third),
                # then relabel ticks to show the true 0-1 scale.
                ax2 = ax.twinx()
                # Prepend a zero anchor one year before the pre-treatment period and
                # end at the last pre-treatment year (no explicit zero at treatment
                # year). This closes the polygon with a vertical right wall at the
                # last pre-treatment year, matching Stata's twoway area behaviour.
                pre_years = t_span[:T0]
                anchor_year = pre_years[0] - 1
                lambda_times = np.concatenate([[anchor_year], pre_years])
                lambda_values = np.concatenate([[0], lambda_hat])
                ax2.fill_between(lambda_times, 0, lambda_values, alpha=0.6, color="#556B2F")
                ax2.set_ylim(0, 3)
                ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
                ax2.set_yticklabels(["0.0", "0.3", "0.5", "0.8", "1.0"])
                ax2.set_ylabel("Lambda weight")
            # Extend x-axis 3 years to the left so small pre-treatment triangles are
            # not clipped at the edge (mirrors Stata's default padding behaviour).
            ax.set_xlim(t_span[0] - 3, t_span[-1] + 1)
            ax.axvline(x=times[i], label="", color='r', linestyle="-", lw=.8)

            ax.set_xlabel("Time")
            ax.set_title("Adoption: " + str(time_title_cb(time)));

            # Set y-axis limits AFTER all plotting to match Stata's tick-aligned axis range.
            # Both bottom and top are aligned to the nearest "nice" tick, matching Stata's
            # twoway defaults.  The tick interval is the same one Stata would auto-select
            # for ~4 ticks.  Fallback to a 5% margin when the tick boundary is too far away.
            if axlimit_zero:
                ax.set_ylim(ymin=0)
            else:
                _rng = plot_y_max - plot_y_min
                _rough = _rng / 4.0
                _exp = math.floor(math.log10(_rough))
                _base = 10 ** _exp
                _nf = _rough / _base
                if _nf < 1.5:   _tick = _base
                elif _nf < 3.0: _tick = 2 * _base
                elif _nf < 7.0: _tick = 5 * _base
                else:           _tick = 10 * _base
                # Bottom: use tick_floor when gap ≤ 50% of one tick interval; else
                # use the data minimum directly (no added margin), matching Stata.
                _tick_floor = math.floor(plot_y_min / _tick) * _tick
                if (plot_y_min - _tick_floor) / _tick > 0.5:
                    _y_bot = plot_y_min
                else:
                    _y_bot = _tick_floor
                # Top: use tick_ceil when gap ≤ 75% of one tick interval; else 5% margin.
                _tick_ceil = math.ceil(plot_y_max / _tick) * _tick
                if (_tick_ceil - plot_y_max) / _tick > 0.75:
                    _y_top = plot_y_max + 0.05 * _rng
                else:
                    _y_top = _tick_ceil
                ax.set_ylim(bottom=_y_bot, top=_y_top)

            # plots[f"t_{time}"] = fig
            plots.append(fig)
        self.plot_outcomes = []
        self.plot_outcomes = plots
        return self

    def plot_weights(self, unit_filter=None, times=None, time_title_cb=int):
        weights = self.weights
        table_result = self.att_info
        lambda_wg = weights["lambda"]
        omega_wg = weights["omega"]
        N0s = table_result.N0
        T0s = table_result.T0
        T1s = table_result.T1
        N1s = table_result.N1
        atts = np.round(table_result.att_time, 2)
        y_units = self.Y_units
        Y_setups = self.Y_betas

        if times is None:
            times = table_result.time

        real_att = np.round(self.att, 2)

        # label_size 
        ls = np.arange(0, 114, 1)
        ls_rel = np.interp(ls, (ls.min(), ls.max()), (9, 4))#[len(weights_dots) - 1]
        # ns = ls_rel[0]
        if unit_filter is not None: 
            l_unit_f = len(unit_filter)
            if l_unit_f > 114:
                ns = ls_rel[113]
            ns = ls_rel[l_unit_f - 1]
        plots = []
        def plot_times(i):
            
            N0, T0, N1, T1 = N0s[i], T0s[i], N1s[i], T1s[i]

            units = y_units[i][:N0]
            ns = ls_rel[len(units) - 1]
            Y = Y_setups[i].to_numpy()

            lambda_hat = lambda_wg[i]
            omega_hat = omega_wg[i]
            lambda_pre = np.concatenate((lambda_hat, np.full(T1, 0)))
            lambda_post = np.concatenate((np.full(T0, 0), np.full(T1, 1 / T1)))
            omega_control = np.concatenate((omega_hat, np.full(N1, 0)))
            omega_treat = np.concatenate((np.full(N0, 0), np.full(N1, 1 / N1)))

            difs = np.dot(omega_treat, Y).dot(lambda_post - lambda_pre) -\
                np.dot(Y[:N0, :], (lambda_post - lambda_pre))
            size_dot = omega_hat / np.max(omega_hat) * 10
            color_dot = np.where(size_dot == 0, "#9D0924", "#2897E2")
            # shape_dot = np.where(size_dot == 0, ".", "v")
            spaces = " " * (len(str(int(times[i]))) + 1)
            import matplotlib.pyplot as plt

            size_dot = np.interp(size_dot, (size_dot.min(), size_dot.max()), (1, 50))

            weights_dots = pd.DataFrame({
                "unit": units, "difs": difs, "size": size_dot, 
                # "shape": shape_dot, 
                "color": color_dot
                })

            if unit_filter is not None:
                weights_dots = weights_dots.query("unit in @unit_filter")
                size_dot = weights_dots.size
                size_dot = np.interp(size_dot, (size_dot.min(), size_dot.max()), (1, 50))
                weights_dots["size_dot"] = size_dot

            weights_dots = weights_dots.reset_index(drop=True)
            weights_dots["pos"] = np.arange(len(weights_dots))

            fig, ax = plt.subplots(figsize=(max(6, len(weights_dots) * 0.28), 5))

            ax.scatter("pos", "difs", data=weights_dots, s="size", c="color", label="")
            ax.set_xticks(weights_dots["pos"])
            ax.set_xticklabels(weights_dots["unit"], rotation=90, fontsize=ns)
            ax.set_xlim(-0.8, len(weights_dots) - 0.2)
            fig.tight_layout()
            ax.set_xlabel("Group")
            ax.set_ylabel("Difference")
            ax.set_title("Adoption: " + str(time_title_cb(times[i])))
            ax.axhline(y=atts[i], linestyle = "--", color = "#E00029", lw = .6, label = f"Att {time_title_cb(times[i])}: {atts[i]}")
            ax.axhline(y=self.att, linestyle = "--", color = "#640257", lw = .8, label = f"Att: {spaces} {real_att}")
            ax.legend(fontsize = 9);
            if weights_dots.difs.max() > 0 and weights_dots.difs.min() < 0:
                ax.axhline(y=0, lw = .5, c = "#0D3276");
            plots.append(fig);

        for i, time in enumerate(times):
            plot_times(i)
        self.plot_weights = []
        self.plot_weights = plots
        return self
