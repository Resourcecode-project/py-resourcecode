%**************************************************************************
%                       ReourceCODE Project
%
%   Identification of weather windows
%   Montly statistics
%
%   NMI Method
%
%   Based on EQUIMAR Deliverable D7.4.1
%   Procedures for Estimating Site Accessibility and
%   Appraisal of Implications of Site Accessibility
%   (T. Stallard,University of Manchester, UKJ-F. Dhedin, Sylvain Saviot 
%   and Carlos NogueraElectricit� de France, France)
%   August 2010
%
%   and
%
%  Walker RT, Johanning L, Parkinson R. (2011) Weather Windows for Device 
%  Deployment at UK test Site: Availability and Cost Implications, 
%  European Wave and Tidal Energy Conference, Southampton,  EWTEC2011. 
%
%**************************************************************************
%
% Input:
%
%       mtime:  date and time vector - Matlab date format
%       Hs:     Significant Wave Height (m)
%       Ha:     Significant wave height operational access threshold (m)
%       Wdur:   Operation weather window duration (Hours)
%
%
% Output:
%
%       Wbl:    Weibull adjustment parameters [x0, b0, k0]
%       Tau:    Persistence: Mean duration of periods for which Hs<Ha (Hours)
%       Ne:     Number of events
%       At:     Access time (Hours)
%       Wt:     Waiting time (Hours)
%
%**************************************************************************
%
%hsref : file contains example hs vector and associated time vector 
%        mtime: 1 hour time step - matlab format

% load hsref;
load test;

%monthvec : used for plots legends
monthvec = ['January  ';...
            'February '; ...
            'March    '; ...
            'April    '; ...
            'May      '; ...
            'June     '; ...
            'July     '; ...
            'August   '; ...
            'September'; ...
            'October  '; ...
            'November '; ...
            'December ' ];

% Thresholds used for plots       
Tref = [24;48;72];
Href = [1;2;3];
Ha = 1:0.5:3; 

%******************************************
% Matrix of months indices over the years
%******************************************

%nyear: number of years in the time series
ydeb = str2double(datestr(mtime(1),10));
yfin = str2double(datestr(mtime(end),10));
nyear = yfin-ydeb+1;

nmonth = 12;

itest = datenum(datestr(mtime,'yyyy-mm'), 'yyyy-mm');
ditest = diff(itest);
iref = find(ditest>1);

%imyd: indices of months start in time series
imyd = [1; iref+1];

%imyd: indices of months end in time series
imyf = [iref; length(mtime)];

%hsmy: (12,nyear) matrix of hs
%mtmy: (12,nyear) matrix of associated times

for imo = 1:12
    hsy = []; mty = [];

    for ind = 1:nyear
        imy = (ind-1)*12+imo;
        hsy = [hsy hs(imyd(imy):imyf(imy))'];
        mty = [mty mtime(imyd(imy):imyf(imy))];
    end;
    ly = length(hsy);
    hsmy(imo,1:ly) = hsy;
    mtmy(imo,1:ly) = mty;
end;

%********************************************************
%Calcul des distributions et weather windows mensuelles 
%********************************************************

Tau = zeros(12,744);
Taui = 1:744;

for imonth = 1:12
    clear hs;
    hs0 = hsmy(imonth,:);
    i0 = find(hs0,1,'last');
    hs = hs0(1:i0);
    hsmax = max(hs);

    Duree = length(hs)./nyear;

%*****************************************
% Hs cumulative distribution
%*****************************************
    dbin = 0.1;
    edge = [min(hs):dbin:hsmax+dbin];
    bin = 0.5*(edge(1:end-1)+edge(2:end));

    [NHs, BinHs] = histc(hs,edge);
    FrHs = NHs./length(hs);
    CFrHs = cumsum(FrHs);

    MCFrHs = 1.-CFrHs;
    MCFrHs(MCFrHs <= 0) = 1.0e-9;

    clear edge;
    edge = bin;

%******************************************************
% Weibull parameters assessment (x0,b,k)
%******************************************************

    Y = log(log(1./MCFrHs));

    dx = 0.005; x00 = 0.; 
    R = 0.; R0 = 0.1;
    k0 = 0; b0 = 0;

    while R0>R
        R = R0;
        k(imonth) = k0;
        b(imonth) = b0;
        x0(imonth) = x00-dx;
        x00 = x00+dx;
        X = log(bin-x00);
        [f0,G] = fit(X',Y','poly1');
        R0 = G.rsquare;
        k0 = f0.p1;
        b0 = exp(-f0.p2/k0);
    end;


    P = exp(-((bin-x0(imonth))./b(imonth)).^k(imonth));

%*************************************************
% Mean duration of events with Hs<Ha
%*************************************************

    Hm(imonth) = b(imonth)*gamma(1.+1./k(imonth))+x0(imonth);
    gam(imonth) = k(imonth)+1.8*x0(imonth)/(Hm(imonth)-x0(imonth));
    beta(imonth) = 0.6*gam(imonth)^0.287;
    A(imonth) = 35./sqrt(gam(imonth));

    Taunum = A(imonth)*(1.-P);
    Tauden = P.*(-log(P)).^beta(imonth);
    Tau(imonth,1:length(edge)) = Taunum./Tauden;


    for ind = 1:length(Ha)  
        [dedge,iedge] = min(abs(edge-Ha(ind)));
        TT = Tau(imonth,iedge);
        xi = Taui./TT;

        %Probabilit that Hs<Ha persists over normalised duration xi
        alfa(imonth) = 0.267*gam(imonth)*(Ha(ind)./Hm(imonth)).^-0.4;
        C(imonth) = (gamma(1.+1./alfa(imonth))).^alfa(imonth);
        Pxi = exp(-C(imonth)*(xi.^alfa(imonth)));

        ePa = (Ha(ind)-x0(imonth))./b(imonth);
        ePak = ePa.^k(imonth);
        Pa = exp(-ePak);
        PT(ind,:) = Pxi.*(1.-Pa);

        % Number of events with Hs<Ha and Duration<T - monthly
        Ni(imonth,ind,:) = Duree*Pxi.*(1-Pa)./Taui;

        %mean duration of access time - monthly
        Nac(imonth,ind,:) = Duree*PT(ind,:);

        %mean duration of waiting time - monthly
        Nwa(imonth,ind,:) = (Duree-Nac(imonth,ind,:))./Ni(imonth,ind,:);
        iD = find(Nwa(imonth,ind,:)>Duree);
        Nwa(imonth,ind,iD) = Duree;

    end;
    %***************************************************
    % Plots (monthly and (6x2) multiplots over 12 months
    %***************************************************
    figure(5)
    hold off;
    subplot(211)
    plot(edge,P,edge,MCFrHs,'r+');
    le = sprintf('x0=%8.5f, b=%8.5f, k=%8.5f ',x0(imonth),b(imonth),k(imonth));
    le1 = legend(le);
    set(le1,'fontsize',5);
    title(['Weibull 3p fit -  ' monthvec(imonth,:)]);
    xlabel('Significant Wave Height (m)'); ylabel('Probability of Exceedance');
    subplot(212)
    plot(X,Y,'+',X,log(log(1./P)));
    xlabel('ln(Hs-x0)');ylabel('ln(ln(1./P))');
    le = sprintf(' R=%9.8f',R);
    le2 = legend(le,'location','southeast');
    set(le2,'fontsize',5);
    saveas(gca,['wbl3pfit_' monthvec(imonth,1:3)],'png');
    close(5);

    figure(1)
    subplot(6,2,imonth)
    plot(edge,MCFrHs,'r+',edge,P,'markersize',1);
    hold on;
    axis([0 ceil(hsmax) 0 1]);
    set(gca,'fontsize',6);
    le = sprintf(' x0=%8.5f \n b=%8.5f \n k=%8.5f \n R=%6.4f ',x0(imonth),b(imonth),k(imonth),R);
    le1 = legend(le,'location','northeast');
    set(le1,'fontsize',5);
    ti = title(['Weibull 3p fit  ' monthvec(imonth,:)]);
    set(ti,'fontsize',5);

    if imonth>10
        xlabel('Significant Wave Height (m)'); 
    end;
    yl = ylabel('Prob. of Exceedance');
    set(yl,'fontsize',4);

    orient tall;

    saveas(gca,['year_wbl3pfit' ],'png'); 

    figure(6)
    hold off;
    plot(edge,Tau(imonth,1:length(edge)));
    hold on; grid on;
    v = axis; axis([0 10 0 240]);
    xlabel('Significant Wave Height (m)'); ylabel('Mean window Length (Hr)');
    title(['Mean window Length -  ' monthvec(imonth,:)]);
    saveas(gca,['Tau_' monthvec(imonth,1:3)],'png');
    close(6);

    figure(2)
    subplot(4,3,imonth);
    plot(edge,Tau(imonth,1:length(edge)));
    hold on; grid on;
    set(gca,'fontsize',6);
    v = axis; axis([0 10 0 240]);
    if imonth>9;
        xlabel('Significant Wave Height (m)'); 
    end;
    %ylabel('Mean Window Length (Hr)');
    ylabel('(Hours)');
    ti = title(['Mean window Length - ' monthvec(imonth,:)]);

    set(ti,'fontsize',5);
    orient landscape;
    saveas(gca,'Year_Tau','png');

    figure(7)
    hold off;
    plot(Taui(1:6:end),PT(1,1:6:end),'-o',Taui(1:6:end),PT(2,1:6:end),'-x',Taui(1:6:end),PT(3,1:6:end),'-+',Taui(1:6:end),PT(4,1:6:end),'-*',Taui(1:6:end),PT(5,1:6:end),'-s','markersize',3);
    hold on; grid on;
    set(gca,'XTickLabel',[0:24:144]);
    axis([0 120 0 1]);
    xlabel('Duration of Weather Window (Hrs)');
    ylabel('Probability of Occurrence');
    legend('1.0 m','1.5 m','2.0 m','2.5 m','3.0 m'); 
    title(['Probability of Occurrence - ' monthvec(imonth,:)]);
    saveas(gca,[ 'Probdur_' monthvec(imonth,1:3)],'png');
    close(7);

    figure(3)
    subplot(6,2,imonth)
    plot(Taui(1:6:end),PT(1,1:6:end),'-o',Taui(1:6:end),PT(2,1:6:end),'-x',Taui(1:6:end),PT(3,1:6:end),'-+',Taui(1:6:end),PT(4,1:6:end),'-*',Taui(1:6:end),PT(5,1:6:end),'-s','markersize',3);
    hold on; grid on;
    set(gca,'fontsize',6);
    set(gca,'XTickLabel',0:24:144);
    axis([0 120 0 1]);
    if imonth>10 
        xlabel('Duration of Weather Window (Hrs)');
    end;
        ylabel('Prob. of Occurrence');
    legend('1.0 m','1.5 m','2.0 m','2.5 m','3.0 m'); 
    title(['Probability of Occurrence -  ' monthvec(imonth,:)]);
    orient tall
    saveas(gca,'Year_Probdur','png');
end;


%***********************************************************************
% Additional plots
% monthly evolution of number of events, Access time and Waiting time
% for weather windows corresponding to Hs < Href and duration < Tref
%***********************************************************************

for iT = 1:3
    iTaui = find(Taui==Tref(iT));
    for iH = 1:3
        iHa = find(Ha==Href(iH));
        figure(8)
        hold off;
        subplot(311)
        plot(Ni(:,iHa,iTaui));
        hold on; grid on;
        set(gca,'XLim',[1 12],'XTickLabel',monthvec(:,1:3));
        ylabel('Number of Events');
        titre = sprintf(' - Number of Events - Hs=%6.2f m, %3d hr Window',Ha(iHa),Taui(iTaui) );
        title(titre);
        subplot(312)
        plot(Nac(:,iHa,iTaui));
        hold on; grid on;
        set(gca,'XLim',[1 12],'XTickLabel',monthvec(:,1:3));
        ylabel('Hours');
        titre = sprintf(' - Access Time - Hs=%6.2f m, %3d hr Window',Ha(iHa),Taui(iTaui) );
        title(titre);
        subplot(313)
        plot(Nwa(:,iHa,iTaui),'r--');
        hold on; grid on;
        set(gca,'XLim',[1 12],'XTickLabel',monthvec(:,1:3)); 
        ylabel('Hours');
        titre = sprintf(' - Waiting Time - Hs=%6.2f m, %3d hr Window',Ha(iHa),Taui(iTaui) );
        title(titre);
        orient tall;
        saveas(gca,['Na_'  num2str(Ha(iHa)) '_' num2str(Taui(iTaui))],'png');
        close(8);
    end;
end;
