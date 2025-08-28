# cell_cycle

a set of analysis run on 


# details

\clearpage
\section{Methods}

\subsection{Experiment Overview}

\noindent 
\textbf{Goal:}
We aim to capture single-cell long-read gene expression for BJ fibroblasts sampled at various points during their progression through the cell cycle (Figure \ref{fig:experiment1}). Cross-ref: \href{https://docs.google.com/spreadsheets/d/1P2MAqlTtmPun7EwLS5uyWpPUq8r6cOB_cqZz0_sG-Uc/edit?usp=sharing}{DAI\#2.5 calculations}




\begin{figure}[!tbh]
    \centering
    \fbox{\includegraphics[width=0.7\linewidth]{figures/experiement1.png}}
    \caption{\textbf{Overview of Cell Cycle Experiment.}}
    \label{fig:experiment1}
\end{figure}


\subsection{Cell Culture}
Unsynchronized BJ fibroblast cells  (passage 5) we grown according to \href{https://docs.google.com/document/d/1d1CLh6IE6PIOwhh80YKMYrCokqGB0YG6F093MyZDuT0/edit}{DAI\#2.5 Fibroblast Unsynched Single Cell Transcriptomics (2.510)}

\subsection{Cell Sorting}
BJ fibroblasts were FACS sorted into three cell cycle phases using total genomic content (Figure \ref{fig:cell_sort}). Sorting documentation may be found in \href{https://docs.google.com/document/d/1d1CLh6IE6PIOwhh80YKMYrCokqGB0YG6F093MyZDuT0/edit}{DAI\#2.5 Fibroblast Unsynched Single Cell Transcriptomics}. Sorting data may be found here: \href{https://drive.google.com/drive/u/1/folders/1hGYMWiKU1AzyiKJMmJ9jW8nh30TKG8AR}{B3IRo71624 Hoechst} on Google Drive. Additionally, see \href{https://flowcytometry-embl.de/wp-content/uploads/2016/12/Hoechst-staining-.pdf}{Hoechst 33342 Staining for Cell Cycle Analysis of Live Cells.}

\begin{figure}[!tbh]
    \centering
    \captionsetup{width=.55\linewidth}
    \fbox{\includegraphics[width=0.55\linewidth]{figures/cell_sort.png}}
    \caption{\textbf{Cell sorting into Cell Cycle Phases.} Sorting (FACS) was performed on cells stained with 16 uM Hoechst 33342 for 50 minutes at 37C. Left-most gate is G1, the middle gate is S, and the right-most gate is G2/Md.
    }
    \label{fig:cell_sort}
\end{figure}


\subsection{Feature Barcoding (Cell Cycle)}
Cells in each phase were barcoded using cell hashing protocol described in  \href{https://docs.google.com/document/d/1lecr-1T1md_TmaaAf8f3G48CITmgVyJEx6683ZEQWAI/edit}{Protocol\_Cell Hashing with Single Cell Barcoding}.  Briefly, Biolegend feature antibodies were added to the pooled, sorted single-cell cultures prior to 10X barcoding and ONT sequencing prep.


\subsection{10X Single-cell Library Preparation}
Single cells were submitted to the UM AGC and prepared using \href{https://drive.google.com/file/d/1s1OeKQxu4zaOlhA5Hx-yY-LKKw_FEExJ/view}{Chromium GEM-X Single Cell 3' Reagent Kits v4}.  The UM AGC returned two prepared libraries: (1) a transcript library with cell barcodes and transcripts, (2) a Biolegend cell hash library with surface expression of feature barcodes and 10X cell barcodes (Figure \ref{fig:10x_prep}).
