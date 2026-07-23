#!/usr/bin/env python3
"""Regenerate the honest improvement curve from iterative_result.json"""
import json, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
d=json.load(open("out/iterative_result.json")); curve=d["cv_curve"]
iters=[c["iter"] for c in curve]; cv=[c["cv_macro_f1"] for c in curve]; kept=[c.get("kept",True) for c in curve]
best=[]; b=-1
for c in curve:
    if c["iter"]==0: b=c["cv_macro_f1"]
    elif c.get("kept"): b=max(b,c["cv_macro_f1"])
    best.append(b)
fig,ax=plt.subplots(figsize=(9,5.2))
for it,v,k in zip(iters,cv,kept):
    ax.scatter(it,v,s=70,c=("#1E7A46" if (k or it==0) else "#BBBBBB"),zorder=3,edgecolors="white",linewidths=1)
ax.plot(iters,best,color="#2E6DA4",lw=2.5,zorder=2,label="Best kept (CV macro-F1)")
ax.plot(iters,cv,color="#CCCCCC",lw=1,ls="--",zorder=1,label="Each trial (incl. rejected)")
ax.axhline(0.788,color="#9A6A00",lw=1.3,ls=":",zorder=1)
ax.text(11,0.792,"best prior model 0.788 (test acc)",color="#9A6A00",fontsize=8,ha="right")
ax.set_xlabel("Iteration"); ax.set_ylabel("Cross-validation macro-F1")
ax.set_title("Honest iterative improvement: CV-driven, plateaus after 2 gains",color="#1F3A5F",weight="bold")
ax.set_ylim(0.58,0.80); ax.grid(True,alpha=0.25); ax.legend(loc="lower right",fontsize=9)
plt.tight_layout(); plt.savefig("out/improvement_curve.png",dpi=150,bbox_inches="tight")
print("saved out/improvement_curve.png")
