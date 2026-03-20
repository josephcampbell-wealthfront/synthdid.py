"""
Export Stata omega and lambda weights to CSV for SDID, SC, DiD methods.
Run with: python export_stata_weights.py
"""
import subprocess, os

STATA_EXE = r'C:\Program Files\Stata17\StataMP-64.exe'
WORK_DIR  = r'C:\Users\ronco\AppData\Local\Temp\stata_sdid'

do_code = r"""
use "cigar.dta", clear

local methods sdid sc did
local mnames  sdid sc  did

forvalues mi = 1/3 {
    local mname : word `mi' of `mnames'
    local mopt  : word `mi' of `methods'

    if "`mopt'" == "sdid" {
        sdid sales state year treatment, vce(noinference)
    }
    else {
        sdid sales state year treatment, vce(noinference) method(`mopt')
    }

    mata:
        omega   = st_matrix("e(omega)")
        lambda  = st_matrix("e(lambda)")
        mname   = "`mname'"

        // --- omega ---
        fh = fopen("omega_" + mname + ".csv", "w")
        fput(fh, "cohort,state,omega")
        cohorts = (1975, 1976, 1978, 1979, 1981, 1983, 1986)
        nrow = rows(omega) - 1
        for (c=1; c<=7; c++) {
            for (r=1; r<=nrow; r++) {
                sid = omega[r, 8]
                w   = omega[r, c]
                fput(fh, strofreal(cohorts[c]) + "," + strofreal(sid) + "," + strofreal(w))
            }
        }
        fclose(fh)

        // --- lambda ---
        fh = fopen("lambda_" + mname + ".csv", "w")
        fput(fh, "cohort,year,lambda")
        nrow_l = rows(lambda) - 1
        for (c=1; c<=7; c++) {
            for (r=1; r<=nrow_l; r++) {
                yr = lambda[r, 8]
                w  = lambda[r, c]
                if (w != .) {
                    fput(fh, strofreal(cohorts[c]) + "," + strofreal(yr) + "," + strofreal(w))
                }
            }
        }
        fclose(fh)
    end
    display "`mname' weights exported"
}
display "All done"
"""

do_path  = os.path.join(WORK_DIR, 'script.do')
log_path = os.path.join(WORK_DIR, 'script.log')
if os.path.exists(log_path):
    os.remove(log_path)
with open(do_path, 'w', encoding='utf-8') as f:
    f.write(do_code)

result = subprocess.run(
    [STATA_EXE, '/b', 'do', 'script.do'],
    cwd=WORK_DIR, capture_output=True, timeout=600
)

with open(log_path, encoding='utf-8', errors='replace') as f:
    log = f.read()
idx = log.find('. do script.do')
print(log[idx:] if idx >= 0 else log[-3000:])
