import { TestBed } from "@angular/core/testing";
import { AppComponent } from "../app.component";
import { Router } from "@angular/router";

describe('app.components', () => {
    let appComponent: AppComponent;

    let routerMock = {
        navigate: jest.fn(),
    }

    beforeEach(() => {
        TestBed.configureTestingModule({
            providers: [
                { provide: Router, useValue: routerMock }
            ]
        });

        appComponent = new AppComponent(routerMock as any);
    });

    it('should create an instance', async() => {
        expect(appComponent).toBeTruthy();
        expect(appComponent.title).toEqual('Vimar GENIALE');
        expect(appComponent.sidebarVisible).toEqual(false);
    });

    it('should toggle sidebar', () => {
        expect(appComponent.sidebarVisible).toEqual(false);
        appComponent.toggleSidebar();
        expect(appComponent.sidebarVisible).toEqual(true);
    });

    it('should close sidebar on mobile', async() => {
        window.innerWidth = 768
        appComponent.closeSidebarOnMobile();
        expect(appComponent.sidebarVisible).toEqual(false);
    })
})