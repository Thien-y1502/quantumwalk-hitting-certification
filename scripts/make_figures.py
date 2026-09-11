from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'results'/'raw'; FIG=ROOT/'results'/'figures'; FIG.mkdir(parents=True,exist_ok=True)

piv=pd.read_csv(ROOT/'results'/'tables'/'paired_evaluations.csv')
families=['path','cycle','grid','barbell','lollipop','random_regular','block_model']
fig,ax=plt.subplots(figsize=(7.2,4.2))
xs=[]; ys=[]
for i,f in enumerate(families):
    vals=piv.loc[piv.family==f,'rooted_gain'].to_numpy()
    jitter=np.linspace(-0.18,0.18,len(vals)) if len(vals)>1 else np.array([0.])
    ax.scatter(np.full(len(vals),i)+jitter,vals,s=12,alpha=.65)
    ax.hlines(np.median(vals),i-.28,i+.28,linewidth=2)
ax.axhline(1.0,linestyle='--',linewidth=1)
ax.set_yscale('log'); ax.set_xticks(range(len(families))); ax.set_xticklabels(['Path','Cycle','Grid','Barbell','Lollipop','Random regular','Block model'],rotation=20,ha='right')
ax.set_ylabel('Global / rooted upper-bound looseness'); ax.set_title('Rooted-floor improvement')
fig.tight_layout(); fig.savefig(FIG/'rooted_improvement.pdf'); fig.savefig(FIG/'rooted_improvement.png',dpi=180); plt.close(fig)

cub=pd.read_csv(RAW/'cubic_runs.csv')
s=cub.groupby('N').ratio.agg(['min','median','max']).reset_index()
fig,ax=plt.subplots(figsize=(5.4,4.0))
ax.fill_between(s.N,s['min'],s['max'],alpha=.2); ax.plot(s.N,s['median'],marker='o',label='median')
coef=np.polyfit(np.log(s.N),np.log(s['median']),1); fit=np.exp(coef[1])*s.N**coef[0]
ax.plot(s.N,fit,linestyle='--',label=f'descriptive fit: N^{coef[0]:.3f}')
ax.set_xscale('log'); ax.set_yscale('log'); ax.set_xlabel('Number of vertices, N'); ax.set_ylabel('H(hard) / H(easy)'); ax.legend(); ax.set_title('Finite cubic separation')
fig.tight_layout(); fig.savefig(FIG/'cubic_separation.pdf'); fig.savefig(FIG/'cubic_separation.png',dpi=180); plt.close(fig)

bad=pd.read_csv(RAW/'bad_proposal_exact.csv')
fig,ax=plt.subplots(figsize=(5.8,4.0))
levels=sorted(bad.sigma.unique())
pos=np.arange(len(levels))
for f,g in bad.groupby('family'):
    g=g.set_index('sigma').loc[levels].reset_index()
    ax.plot(pos,g.width_over_H,marker='o',label=f)
labels=['0','1e-8','1e-6','1e-4','1e-2','1e-1','1']
ax.set_xticks(pos); ax.set_xticklabels(labels)
ax.set_yscale('log'); ax.set_xlabel('Proposal corruption scale, sigma'); ax.set_ylabel('Exact interval width / reference H'); ax.set_title('Theorem 7 stress test'); ax.legend()
fig.tight_layout(); fig.savefig(FIG/'bad_proposal_stress.pdf'); fig.savefig(FIG/'bad_proposal_stress.png',dpi=180); plt.close(fig)

fixed=pd.read_csv(RAW/'fixed_proposal_ablation.csv')
fig,ax=plt.subplots(figsize=(6.5,4.0))
for name,g in fixed.groupby('floor_source'):
    ax.plot(g.family,g.looseness,marker='o',label=name)
ax.set_yscale('log'); ax.tick_params(axis='x',rotation=25); ax.set_ylabel('Frozen-proposal upper-bound looseness'); ax.set_title('Fixed-proposal floor ablation'); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig(FIG/'fixed_proposal_ablation.pdf'); fig.savefig(FIG/'fixed_proposal_ablation.png',dpi=180); plt.close(fig)
