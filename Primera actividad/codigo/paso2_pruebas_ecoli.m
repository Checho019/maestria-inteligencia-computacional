%% =======================================================================
%  ECOLI - Pruebas estadisticas sobre las variables (secciones 2 a 11)
%  Ojo: con 336 muestras estamos en el rango donde Shapiro-Wilk es la
%  prueba de normalidad recomendada, por eso es la que manda aca.
% =======================================================================
clear; clc; close all;

base = fileparts(fileparts(mfilename('fullpath')));
addpath(fullfile(base, 'codigo', 'funciones'));
dir_fig = fullfile(base, 'resultados', 'ecoli', 'figuras');
xls     = fullfile(base, 'Resultados_Ecoli.xlsx');
load(fullfile(base, 'resultados', 'ecoli', 'ecoli_crudo.mat'));

alfa = 0.05;

% lillietest y adtest avisan cuando el p-valor se sale de su tabla interna;
% para nosotros basta con saber que p < 0.001, asi que apagamos el aviso.
warning('off','stats:lillietest:OutOfRangePLow');
warning('off','stats:adtest:OutOfRangePLow');

Xc   = T{:, contin};                 % solo las continuas
nc   = numel(contin);

% clases con suficientes muestras para hacer pruebas por grupo.
% imL(2), imS(2) y omL(5) se dejan fuera de las pruebas por clase: con n<10
% ninguna prueba tiene potencia y varias ni siquiera se pueden calcular.
[cnt, nom] = groupcounts(y);
clases_ppal = nom(cnt >= 20);
mask_ppal   = ismember(y, clases_ppal);
fprintf('Clases usadas en las pruebas por grupo: %s\n', strjoin(clases_ppal', ', '));

%% --- 2. Normalidad (guia seccion 2) ------------------------------------
% Cuatro pruebas a proposito, porque miran cosas distintas:
%   Shapiro-Wilk  -> la de referencia para n < 2000
%   Lilliefors    -> version del KS cuando media y varianza se estiman
%   Anderson-Darling -> mas sensible en las colas
%   DAgostino K2  -> dice si el problema es la asimetria o la curtosis
R = nan(nc, 8);
for j = 1:nc
    x = Xc(:, j);
    [p_sw, W]   = swtest(x);
    [~, p_lil]  = lillietest(x);
    [~, p_ad]   = adtest(x);
    [p_k2, K2]  = dagostino_k2(x);
    R(j, :) = [W, p_sw, p_lil, p_ad, K2, p_k2, skewness(x), kurtosis(x)];
end
Norm = table(contin', R(:,1), R(:,2), R(:,3), R(:,4), R(:,5), R(:,6), R(:,7), R(:,8), ...
    R(:,2) > alfa, ...
    'VariableNames', {'Variable','W_Shapiro','p_Shapiro','p_Lilliefors','p_AndersonD', ...
                      'K2_DAgostino','p_DAgostino','Asimetria','Curtosis','Normal_alfa05'});
disp('--- Normalidad (variable completa) ---'); disp(Norm);

% ahora por clase, que es lo que de verdad importa antes de un ANOVA
filas = {};
for j = 1:nc
    for i = 1:numel(clases_ppal)
        x = Xc(strcmp(y, clases_ppal{i}), j);
        [p_sw, W] = swtest(x);
        filas(end+1, :) = {contin{j}, clases_ppal{i}, numel(x), W, p_sw, p_sw > alfa}; %#ok<SAGROW>
    end
end
NormClase = cell2table(filas, 'VariableNames', ...
    {'Variable','Clase','N','W_Shapiro','p_Shapiro','Normal_alfa05'});
fprintf('Combinaciones variable-clase que pasan normalidad: %d de %d\n', ...
        sum(NormClase.Normal_alfa05), height(NormClase));

%% --- 3. Homocedasticidad (guia seccion 3) ------------------------------
V = nan(nc, 4);
for j = 1:nc
    x = Xc(mask_ppal, j);  g = y(mask_ppal);
    p_lev = vartestn(x, g, 'TestType','LeveneAbsolute', 'Display','off');
    p_bar = vartestn(x, g, 'TestType','Bartlett', 'Display','off');
    V(j, :) = [p_lev, p_lev > alfa, p_bar, p_bar > alfa];
end
Var = table(contin', V(:,1), logical(V(:,2)), V(:,3), logical(V(:,4)), ...
    'VariableNames', {'Variable','p_Levene','Homoced_Levene','p_Bartlett','Homoced_Bartlett'});
disp('--- Homogeneidad de varianzas entre clases ---'); disp(Var);

%% --- 4. Comparacion entre clases, multiclase (guia seccion 5) ----------
% ANOVA (parametrica) y Kruskal-Wallis (no parametrica) para poder comparar
% las dos rutas y justificar cual reportamos.
C = nan(nc, 6);
for j = 1:nc
    x = Xc(mask_ppal, j);  g = y(mask_ppal);
    [p_anova, tbl] = anova1(x, g, 'off');
    F    = tbl{2,5};
    eta2 = tbl{2,2} / tbl{4,2};                     % SSB/SST = tamano del efecto
    [p_kw, tblk] = kruskalwallis(x, g, 'off');
    H = tblk{2,5};
    k = numel(clases_ppal);  n = numel(x);
    eps2 = (H - k + 1) / (n - k);                   % epsilon2 (efecto no parametrico)
    C(j, :) = [F, p_anova, eta2, H, p_kw, eps2];
end
Comp = table(contin', C(:,1), C(:,2), C(:,3), C(:,4), C(:,5), C(:,6), ...
    'VariableNames', {'Variable','F_ANOVA','p_ANOVA','eta2','H_KruskalWallis','p_KruskalWallis','epsilon2'});
disp('--- Comparacion de medias/medianas entre clases ---'); disp(Comp);

% post-hoc sobre la variable con mayor efecto (rangos + correccion Bonferroni)
[~, jmax] = max(C(:,6));
[~,~,st] = kruskalwallis(Xc(mask_ppal, jmax), y(mask_ppal), 'off');
cmp = multcompare(st, 'Display','off', 'CType','bonferroni');
Post = array2table(cmp, 'VariableNames', {'i','j','LimInf','Dif_rangos','LimSup','p_ajustado'});
Post.Grupo_A  = clases_ppal(cmp(:,1));
Post.Grupo_B  = clases_ppal(cmp(:,2));
Post.Variable = repmat(contin(jmax), height(Post), 1);
Post = Post(:, {'Variable','Grupo_A','Grupo_B','Dif_rangos','LimInf','LimSup','p_ajustado'});
fprintf('Post-hoc (Bonferroni) sobre %s: %d de %d pares salen distintos\n', ...
        contin{jmax}, sum(Post.p_ajustado < alfa), height(Post));

%% --- 5. Variables binarias vs clase (guia seccion 7) -------------------
% lip y chg son binarias, no tiene sentido pasarles pruebas de normalidad.
% Se les aplica chi2 de independencia + V de Cramer.
filas = {};
for j = 1:numel(binar)
    [Vcr, chi2v, pv, gl] = cramersv(T.(binar{j}), y);
    tabla = crosstab(T.(binar{j}), y);
    esp = sum(tabla,2)*sum(tabla,1)/sum(tabla(:));
    filas(end+1,:) = {binar{j}, chi2v, gl, pv, Vcr, min(esp(:)), min(esp(:)) >= 5}; %#ok<SAGROW>
end
Cat = cell2table(filas, 'VariableNames', ...
    {'Variable','Chi2','gl','p_valor','V_Cramer','MinEsperado','Cumple_regla_5'});
disp('--- Variables binarias vs clase ---'); disp(Cat);

%% --- 6. Correlacion y multicolinealidad (guia secciones 6 y 9) ---------
Rp = corr(Xc, 'type','Pearson');
Rs = corr(Xc, 'type','Spearman');
Rk = corr(Xc, 'type','Kendall');
vif = calcular_vif(Xc);
cond_num = cond(zscore(Xc));

Corr_P = array2table(Rp, 'VariableNames', contin, 'RowNames', contin);
Corr_S = array2table(Rs, 'VariableNames', contin, 'RowNames', contin);
Corr_K = array2table(Rk, 'VariableNames', contin, 'RowNames', contin);
Vif = table(contin', vif, vif > 5, 'VariableNames', {'Variable','VIF','Sospechosa'});
fprintf('Numero de condicion de la matriz estandarizada: %.1f\n', cond_num);
disp('--- VIF ---'); disp(Vif);

[fi, co] = find(triu(abs(Rp), 1) > 0.6);
for i = 1:numel(fi)
    fprintf('Correlacion alta: %s - %s  Pearson=%.3f  Spearman=%.3f\n', ...
        contin{fi(i)}, contin{co(i)}, Rp(fi(i),co(i)), Rs(fi(i),co(i)));
end

f = figure('Visible','off','Position',[100 100 1100 450]);
subplot(1,2,1); imagesc(Rp, [-1 1]); colorbar; axis square;
set(gca,'XTick',1:nc,'XTickLabel',contin,'YTick',1:nc,'YTickLabel',contin);
title('Pearson');
for a = 1:nc
    for b = 1:nc
        text(b, a, sprintf('%.2f', Rp(a,b)), 'HorizontalAlignment','center','FontSize',8);
    end
end
subplot(1,2,2); imagesc(Rs, [-1 1]); colorbar; axis square;
set(gca,'XTick',1:nc,'XTickLabel',contin,'YTick',1:nc,'YTickLabel',contin);
title('Spearman');
for a = 1:nc
    for b = 1:nc
        text(b, a, sprintf('%.2f', Rs(a,b)), 'HorizontalAlignment','center','FontSize',8);
    end
end
sgtitle('Ecoli - mapas de calor de correlacion');
guardar_fig(f, dir_fig, '07_correlacion');

%% --- 7. Relevancia de variables frente a la clase (guia seccion 8) -----
% cuatro criterios distintos para no depender de uno solo
% ojo: fscmrmr devuelve los scores en el orden ORIGINAL de las columnas,
% no en el orden del ranking. Para ver el ranking hay que hacer sc(idx).
[idx_mrmr, sc_mrmr] = fscmrmr(Xc, y);
sc_mrmr_ord = sc_mrmr(:);
% cuidado: la PRIMERA salida de relieff son los indices ordenados, no los
% pesos. Los pesos son la segunda salida.
[~, w_relief] = relieff(Xc, y, 10);
Rel = table(contin', C(:,1), C(:,4), sc_mrmr_ord, w_relief', ...
    'VariableNames', {'Variable','F_ANOVA','H_KruskalWallis','Score_MRMR','Peso_ReliefF'});
Rel.Rank_ANOVA  = ranking(C(:,1));
Rel.Rank_KW     = ranking(C(:,4));
Rel.Rank_MRMR   = ranking(sc_mrmr_ord);
Rel.Rank_Relief = ranking(w_relief');
disp('--- Relevancia de variables ---'); disp(Rel);

%% --- 8. Outliers (guia seccion 10) -------------------------------------
O = nan(nc, 4);
for j = 1:nc
    x = Xc(:, j);
    q = quantile(x, [0.25 0.75]);  ri = q(2)-q(1);
    n_iqr = sum(x < q(1)-1.5*ri | x > q(2)+1.5*ri);
    z = abs((x - mean(x)) / std(x));
    n_z  = sum(z > 3);
    O(j, :) = [n_iqr, 100*n_iqr/numel(x), n_z, 100*n_z/numel(x)];
end
% Mahalanobis robusto: mira los atipicos en conjunto, no variable por variable
[~, ~, d2] = robustcov(Xc);
umbral = chi2inv(0.975, nc);
n_maha = sum(d2 > umbral);

Out = table(contin', O(:,1), O(:,2), O(:,3), O(:,4), ...
    'VariableNames', {'Variable','N_out_IQR','Pct_IQR','N_out_Zscore','Pct_Zscore'});
disp('--- Outliers univariados ---'); disp(Out);
fprintf('Outliers multivariados (Mahalanobis robusto, chi2 0.975): %d (%.1f%%)\n', ...
        n_maha, 100*n_maha/numel(d2));

f = figure('Visible','off','Position',[100 100 800 450]);
plot(d2, '.', 'MarkerSize', 10); hold on; yline(umbral, 'r--', 'umbral chi2 0.975');
xlabel('muestra'); ylabel('distancia de Mahalanobis robusta al cuadrado');
title('Ecoli - deteccion de atipicos multivariados');
guardar_fig(f, dir_fig, '08_mahalanobis');

%% --- 9. PCA para ver separabilidad global (guia seccion 13.7) ----------
[~, score, ~, ~, expl] = pca(zscore(Xc));
f = figure('Visible','off','Position',[100 100 1100 450]);
subplot(1,2,1);
gscatter(score(:,1), score(:,2), y, [], 'o', 6);
xlabel(sprintf('CP1 (%.1f%%)', expl(1))); ylabel(sprintf('CP2 (%.1f%%)', expl(2)));
title('Proyeccion en las 2 primeras componentes'); grid on;
subplot(1,2,2);
bar(expl); hold on; plot(cumsum(expl), '-o', 'LineWidth', 1.2);
xlabel('componente'); ylabel('% de varianza'); legend('individual','acumulada','Location','east');
title('Varianza explicada'); grid on;
sgtitle('Ecoli - PCA sobre las variables continuas');
guardar_fig(f, dir_fig, '09_pca');

%% --- 10. Exportar ------------------------------------------------------
writetable(Norm,      xls, 'Sheet', 'E2_Normalidad');
writetable(NormClase, xls, 'Sheet', 'E2_Normalidad_clase');
writetable(Var,       xls, 'Sheet', 'E2_Varianzas');
writetable(Comp,      xls, 'Sheet', 'E2_Comparacion');
writetable(Post,      xls, 'Sheet', 'E2_PostHoc');
writetable(Cat,       xls, 'Sheet', 'E2_Categoricas');
writetable(Corr_P,    xls, 'Sheet', 'E2_Corr_Pearson',  'WriteRowNames', true);
writetable(Corr_S,    xls, 'Sheet', 'E2_Corr_Spearman', 'WriteRowNames', true);
writetable(Corr_K,    xls, 'Sheet', 'E2_Corr_Kendall',  'WriteRowNames', true);
writetable(Vif,       xls, 'Sheet', 'E2_VIF');
writetable(Rel,       xls, 'Sheet', 'E2_Relevancia');
writetable(Out,       xls, 'Sheet', 'E2_Outliers');

save(fullfile(base,'resultados','ecoli','ecoli_pruebas.mat'), ...
     'Norm','Var','Comp','Rel','Out','vif','cond_num','clases_ppal','n_maha');
fprintf('\nPaso 2 (pruebas estadisticas) terminado.\n');


function r = ranking(v)
% posicion de cada valor de mayor a menor (1 = el mas relevante)
[~, orden] = sort(v, 'descend');
r = zeros(numel(v), 1);
r(orden) = 1:numel(v);
end
