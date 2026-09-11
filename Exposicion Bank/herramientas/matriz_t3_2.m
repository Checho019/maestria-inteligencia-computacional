function matriz_t3_2
% Matriz de confusion de validacion de T3_2 con Fine KNN, conteos tomados de Classification Learner
C = [33580 6088; 1229 38439];
f = figure('Position', [100 100 700 680]);
f.Theme = 'dark';
cc = confusionchart(C, {'no','yes'});
cc.Title = 'Sobremuestreo con Fine KNN';
cc.XLabel = 'Predicted Class';  cc.YLabel = 'True Class';
cc.FontSize = 14;
exportgraphics(f, fullfile('figuras', 'fig08_matriz_t3_2.png'), 'Resolution', 150)
close(f)
end
